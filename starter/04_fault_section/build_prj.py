"""Write the TH2M project file for the 2D plane-strain section with a fault band.

Five materials (MaterialIDs): 0 overburden, 1 caprock, 2 reservoir,
3 underburden, 4 fault band. Same fluids (H2, brine) as the radial model.
Stresses are computed as CHANGES from the initial state (no gravity, no
initial stress): by linear elasticity the in-situ stress is added afterwards
in coulomb.py (superposition).

Usage: python build_prj.py [--bracket drainage|imbibition] [--set key=value ...]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pyvista as pv

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / "common"))
import props  # noqa: E402
import schedule  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--bracket", choices=["drainage", "imbibition"], default="drainage")
ap.add_argument("--set", nargs="*", default=[])
ap.add_argument("--tag", default="")
ap.add_argument("--cycles", type=int, default=1)
a = ap.parse_args()
P = props.load(a.set)
P["n_cycles"] = a.cycles

S_Lr = P["res_S_Lr"]
S_gr = P["res_S_gr_drain"] if a.bracket == "drainage" else props.land_trapped(1 - S_Lr, P["land_C"])
pc0 = props.vg_pc(P["S_L_init"], P["res_vG_pb"], P["res_vG_m"], S_Lr, S_gr)

# initial capillary pressure: the same value everywhere = capillary equilibrium.
# Seals have a high capillary scale pressure (cap_vG_pb) and therefore stay
# > 99.5 % brine-saturated. A negative pc (no gas phase at all) in the seals made
# the linear solver fail (tested), see DECISIONS.md D12.
dom = pv.read(here / "mesh" / "domain.vtu")
dom.point_data["pc_init"] = np.full(dom.n_points, pc0)
dom.save(here / "mesh" / "domain.vtu")

well = pv.read(here / "mesh" / "well.vtu")
H = well.bounds[3] - well.bounds[2]
q = 0.5 * P["line_rate"] / H          # half the well rate enters the half-section
Sch = schedule.build(P, q)

# rock properties per MaterialID: (k, phi, E, nu, S_Lr, S_gr, p_b)
rocks = {
    0: (P["ob_permeability"], P["ob_porosity"], P["ob_E"], P["ob_nu"], P["cap_S_Lr"], 0.0, P["cap_vG_pb"]),
    1: (P["cap_permeability"], P["cap_porosity"], P["cap_E"], P["cap_nu"], P["cap_S_Lr"], 0.0, P["cap_vG_pb"]),
    2: (P["res_permeability"], P["res_porosity"], P["res_E"], P["res_nu"], S_Lr, S_gr, P["res_vG_pb"]),
    3: (P["ob_permeability"], P["ob_porosity"], P["ob_E"], P["ob_nu"], P["cap_S_Lr"], 0.0, P["cap_vG_pb"]),
    4: (P["flt_permeability"], P["flt_porosity"], P["flt_E"], P["flt_nu"], S_Lr, S_gr, P["res_vG_pb"]),
}
m_vg = P["res_vG_m"]


def c(n, v):
    return f"<property><name>{n}</name><type>Constant</type><value>{v}</value></property>"


fluids = f"""
            <phase><type>AqueousLiquid</type>
                <components>
                    <component><name>H2</name><properties>
                        {c("specific_heat_capacity", 14300)}{c("henry_coefficient", P["H2_henry"])}
                        {c("diffusion", P["H2_diff_liquid"])}{c("specific_latent_heat", 0)}
                    </properties></component>
                    <component><name>W</name><properties>{c("specific_heat_capacity", 4187)}</properties></component>
                </components>
                <properties>
                    {c("thermal_conductivity", 0.6)}
                    <property><name>density</name><type>Linear</type><reference_value>{P["brine_density"]}</reference_value>
                        <independent_variable><variable_name>liquid_phase_pressure</variable_name>
                            <reference_condition>{P["p_init"]}</reference_condition><slope>{P["brine_compressibility"]}</slope></independent_variable>
                        <independent_variable><variable_name>concentration</variable_name>
                            <reference_condition>0</reference_condition><slope>{P["H2_M"] / P["brine_density"]:.6e}</slope></independent_variable>
                    </property>
                    {c("viscosity", P["brine_viscosity"])}
                </properties>
            </phase>
            <phase><type>Gas</type>
                <components>
                    <component><name>H2</name><properties>{c("molar_mass", P["H2_M"])}{c("specific_heat_capacity", 14300)}</properties></component>
                    <component><name>W</name><properties>
                        {c("molar_mass", 0.018015)}{c("specific_heat_capacity", 2000)}{c("specific_latent_heat", 0)}
                        {c("vapour_pressure", 0.0)}{c("diffusion", 0.0)}
                    </properties></component>
                </components>
                <properties>
                    {c("thermal_conductivity", 0.2)}
                    <property><name>density</name><type>IdealGasLawBinaryMixture</type></property>
                    {c("viscosity", P["H2_viscosity"])}
                </properties>
            </phase>"""


def medium(mid, k, phi, E, nu, slr, sgr, pb):
    vg = f"<residual_liquid_saturation>{slr}</residual_liquid_saturation><residual_gas_saturation>{sgr}</residual_gas_saturation>"
    return f"""
        <medium id="{mid}">
            <phases>{fluids}
                <phase><type>Solid</type><properties>
                    {c("density", P["rho_solid"])}{c("thermal_conductivity", 3.0)}
                    {c("specific_heat_capacity", 800)}{c("thermal_expansivity", 0)}
                </properties></phase>
            </phases>
            <properties>
                {c("permeability", k)}{c("porosity", phi)}{c("biot_coefficient", P["biot"])}{c("tortuosity", 1)}
                <property><name>saturation</name><type>SaturationVanGenuchten</type>{vg}<p_b>{pb}</p_b><exponent>{m_vg}</exponent></property>
                <property><name>relative_permeability</name><type>RelativePermeabilityVanGenuchten</type>{vg}<exponent>{m_vg}</exponent>
                    <minimum_relative_permeability_liquid>1e-12</minimum_relative_permeability_liquid></property>
                <property><name>relative_permeability_nonwetting_phase</name><type>RelativePermeabilityNonWettingPhaseVanGenuchtenMualem</type>{vg}
                    <exponent>{m_vg}</exponent><min_relative_permeability>1e-9</min_relative_permeability></property>
                <property><name>thermal_conductivity</name><type>EffectiveThermalConductivityPorosityMixing</type></property>
                <property><name>bishops_effective_stress</name><type>BishopsPowerLaw</type><exponent>1</exponent></property>
            </properties>
        </medium>"""


media = "".join(medium(i, *r) for i, r in rocks.items())
E_by_id = " ".join(str(rocks[i][2]) for i in range(5))
nu_by_id = " ".join(str(rocks[i][3]) for i in range(5))
name = f"section_{a.bracket}{('_' + a.tag) if a.tag else ''}"
times = " ".join(f"{x:.1f}" for x in schedule.output_times(Sch, every_days=30))
prj = f"""<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- Generated by build_prj.py. bracket={a.bracket} S_gr={S_gr:.4f} pc0={pc0:.1f} Pa q={q:.4e} kg/m2/s -->
<OpenGeoSysProject>
    <meshes>
        <mesh>mesh/domain.vtu</mesh><mesh>mesh/well.vtu</mesh><mesh>mesh/left.vtu</mesh>
        <mesh>mesh/right.vtu</mesh><mesh>mesh/bottom.vtu</mesh>
    </meshes>
    <processes><process>
        <name>TH2M</name><type>TH2M</type><integration_order>2</integration_order>
        <constitutive_relation><type>LinearElasticIsotropic</type>
            <youngs_modulus>E</youngs_modulus><poissons_ratio>nu</poissons_ratio></constitutive_relation>
        <jacobian_assembler><type>CentralDifferences</type><epsilons>0.01 0.01 1e-06</epsilons></jacobian_assembler>
        <process_variables>
            <gas_pressure>gas_pressure</gas_pressure><capillary_pressure>capillary_pressure</capillary_pressure>
            <temperature>temperature</temperature><displacement>displacement</displacement>
        </process_variables>
        <secondary_variables>
            <secondary_variable name="sigma"/><secondary_variable name="sigma_total"/>
            <secondary_variable name="saturation"/><secondary_variable name="gas_density"/>
            <secondary_variable name="liquid_density"/><secondary_variable name="porosity"/>
            <secondary_variable internal_name="mass_fraction_liquid" output_name="xmWL"/>
        </secondary_variables>
        <specific_body_force>0 0</specific_body_force>
        <mass_lumping>false</mass_lumping>
    </process></processes>
    <media>{media}
    </media>
    <time_loop>
        <processes><process ref="TH2M">
            <nonlinear_solver>basic_newton</nonlinear_solver>
            <convergence_criterion><type>PerComponentDeltaX</type><norm_type>NORM2</norm_type>
                <abstols>1e-1 1e-1 1e-5 1e-8 1e-8</abstols></convergence_criterion>
            <time_discretization><type>BackwardEuler</type></time_discretization>
            <time_stepping><type>IterationNumberBasedTimeStepping</type>
                <t_initial>0</t_initial><t_end>{Sch["t_end"]:.1f}</t_end>
                <initial_dt>60</initial_dt><minimum_dt>1</minimum_dt><maximum_dt>{3 * schedule.DAY:.0f}</maximum_dt>
                <number_iterations>2 4 8 12 20</number_iterations><multiplier>1.6 1.3 1.0 0.7 0.5</multiplier>
            </time_stepping>
        </process></processes>
        <output>
            <type>VTK</type><prefix>{name}</prefix><suffix>_t_{{:gtime}}</suffix>
            <timesteps><pair><repeat>1</repeat><each_steps>100000000</each_steps></pair></timesteps>
            <variables>
                <variable>gas_pressure</variable><variable>capillary_pressure</variable><variable>displacement</variable>
                <variable>sigma</variable><variable>sigma_total</variable><variable>saturation</variable>
                <variable>gas_density</variable><variable>liquid_density</variable><variable>porosity</variable>
                <variable>xmWL</variable>
            </variables>
            <fixed_output_times>{times}</fixed_output_times>
        </output>
    </time_loop>
    <parameters>
        <parameter><name>E</name><type>Group</type><group_id_property>MaterialIDs</group_id_property>
            {"".join(f"<index_values><index>{i}</index><value>{rocks[i][2]}</value></index_values>" for i in range(5))}</parameter>
        <parameter><name>nu</name><type>Group</type><group_id_property>MaterialIDs</group_id_property>
            {"".join(f"<index_values><index>{i}</index><value>{rocks[i][3]}</value></index_values>" for i in range(5))}</parameter>
        <parameter><name>zero</name><type>Constant</type><value>0</value></parameter>
        <parameter><name>u0</name><type>Constant</type><values>0 0</values></parameter>
        <parameter><name>T0</name><type>Constant</type><value>{P["T_res"]}</value></parameter>
        <parameter><name>pg0</name><type>Constant</type><value>{P["p_init"]}</value></parameter>
        <parameter><name>pc0</name><type>MeshNode</type><mesh>domain</mesh><field_name>pc_init</field_name></parameter>
        <parameter><name>p_bhp_min</name><type>Constant</type><value>{P["p_bhp_min"]}</value></parameter>
        <parameter><name>one</name><type>Constant</type><value>1</value></parameter>
        <parameter><name>h2_flux</name><type>CurveScaled</type><curve>injection_schedule</curve><parameter>one</parameter></parameter>
    </parameters>
    <curves><curve><name>injection_schedule</name>
        <coords>{" ".join(f"{x:.1f}" for x in Sch["coords"])}</coords>
        <values>{" ".join(f"{x:.6e}" for x in Sch["values"])}</values>
    </curve></curves>
    <process_variables>
        <process_variable><name>displacement</name><components>2</components><order>1</order>
            <initial_condition>u0</initial_condition>
            <boundary_conditions>
                <boundary_condition><mesh>left</mesh><type>Dirichlet</type><component>0</component><parameter>zero</parameter></boundary_condition>
                <boundary_condition><mesh>right</mesh><type>Dirichlet</type><component>0</component><parameter>zero</parameter></boundary_condition>
                <boundary_condition><mesh>bottom</mesh><type>Dirichlet</type><component>1</component><parameter>zero</parameter></boundary_condition>
            </boundary_conditions>
        </process_variable>
        <process_variable><name>gas_pressure</name><components>1</components><order>1</order>
            <initial_condition>pg0</initial_condition>
            <boundary_conditions>
                <boundary_condition><mesh>well</mesh><type>Neumann</type><component>0</component><parameter>h2_flux</parameter></boundary_condition>{schedule.dirichlet_windows_xml(Sch, "well", "p_bhp_min")}
            </boundary_conditions>
        </process_variable>
        <process_variable><name>capillary_pressure</name><components>1</components><order>1</order>
            <initial_condition>pc0</initial_condition>
        </process_variable>
        <process_variable><name>temperature</name><components>1</components><order>1</order>
            <initial_condition>T0</initial_condition>
            <boundary_conditions>
                <boundary_condition><mesh>domain</mesh><type>Dirichlet</type><component>0</component><parameter>T0</parameter></boundary_condition>
            </boundary_conditions>
        </process_variable>
    </process_variables>
    <nonlinear_solvers><nonlinear_solver><name>basic_newton</name><type>Newton</type><max_iter>25</max_iter>
        <linear_solver>direct</linear_solver></nonlinear_solver></nonlinear_solvers>
    <linear_solvers><linear_solver><name>direct</name><eigen><solver_type>SparseLU</solver_type><scaling>true</scaling></eigen></linear_solver></linear_solvers>
</OpenGeoSysProject>
"""
(here / f"{name}.prj").write_text(prj)
print(f"wrote {name}.prj: S_gr={S_gr:.3f} pc0={pc0/1e3:.0f} kPa q={q:.3e} kg/m2/s t_end={Sch['t_end']/schedule.DAY:.0f} d")
