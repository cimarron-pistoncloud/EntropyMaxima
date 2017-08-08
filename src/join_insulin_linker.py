# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 19:30:34 2016
@author: noel
"""
import sys
# For debugging in spyder
sys_path = '/home/noel/Projects/Protein_design/EntropyMaxima/src'
charmmdir = '/home/noel/Projects/Protein_design/EntropyMaxima/params/charmm27.ff/'
is_in_path = False
for i in sys.path:
    if i == sys_path:
        is_in_path = True
if not is_in_path:
    sys.path.append('/home/noel/Projects/Protein_design/EntropyMaxima/src')
import numpy as np
from Bio.PDB.PDBParser import PDBParser
import Molecular_Rigid_Manipulations as MRM
from Bio.PDB.PDBIO import PDBIO
import CHARMM_Parser as CP
import pandas as pd
from Bio.PDB import *
# Imput Join chain E shortest link to Chain C, Nterm, residue 31
# using the N, CA, C atoms in rasidue C31 and EX to measure proximity after rotations        
############## INPUTS #################
pdb_parser = PDBParser()
base_dir = '/home/noel/Projects/Protein_design/EntropyMaxima/'
struct_path = base_dir+'examples/Super_Structure/add_hydrogens/insulin_link_ddddk_ab_1rr.pdb'
###############################################################################
# FIX PDB file generated by CHARMM Chain identifier is in different column
inFile = open(struct_path, 'r')
contents = inFile.read()
contents_list = contents.split('\n')
for i in range(len(contents_list)):
    if contents_list[i][0:4] == 'ATOM':
        temp = list(contents_list[i])
        # The following two indexes are off by one becasue list index start at 0, and lines in files at 1.
        temp[21] = temp[72]
        contents_list[i] = ''.join(temp)
outFile = open(struct_path, 'w')
for i in contents_list:
    outFile.write(i+'\n')
outFile.close()
###############################################################################
# dihedral angles obtained from http://www.ccp14.ac.uk/ccp/web-mirrors/garlic/garlic/commands/dihedrals.html
#dihe = {'psi':'N CA C +N','phi':'-C N CA C'}
dihe = {'ALA':{'psi':'N CA C +N','phi':'-C N CA C'},\
        'ARG':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG CD','ch3':'CB CG CD NE',\
               'ch4':'CG CD NE CZ','ch5':'CD NE CZ NH1'},\
        'ASN':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG OD1'},\
        'ASP':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG OD1'},\
        'CYS':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB SG'},\
        'GLU':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG CD','ch3':'CB CG CD OE1'},\
        'GLN':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG',\
               'ch2':'CA CB CG CD','ch3':'CB CG CD OE1'},\
        'GLY':{'psi':'N CA C +N','phi':'-C N CA C'},\
        'HSD':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG ND1'},\
        'HSE':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG ND1'},\
        'HSP':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG ND1'},\
        'ILE':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG1','ch2':'CA CB CG1 CD'},\
        'LEU':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG CD1'},\
        'LYS':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG CD','ch3':'CB CG CD CE',\
               'ch4':'CG CD CE NZ'},\
        'MET':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG SD','ch3':'CB CG SD CE'},\
        'PHE':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG CD1'},\
        'PRO':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG CD'},\
        'SER':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB OG'},\
        'THR':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB OG1'},\
        'TRP':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG CD2'},\
        'TYR':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG','ch2':'CA CB CG CD1'},\
        'VAL':{'psi':'N CA C +N','phi':'-C N CA C','ch1':'N CA CB CG1'}}
###############################################################################
def calculate_dih_angles(sp,mcc_loc,mnp,distance_angles,m):
    # TDOD This method works for two chains with A and B identifiers. Make it more general.
    for i in distance_angles.columns:
        temp_res = i[0:3]
        temp_ang = i[4:7]
        temp_chn = i[8:9]
        if i == 'Distance':
            d1 = mnp.get_vector_list(sp,mcc_loc,m[0],m[2],[m[3]])
            d2 = mnp.get_vector_list(sp,mcc_loc,m[4],m[6],[m[7]])
            distance_angles.loc[mcc_loc,i] = mnp.vector_lists_rmsd(d1,d2)
        elif i == 'Energy':
            eng1 = mnp.model_energy(sp[mcc_loc],m[0],m[1],m[2])
            eng2 = mnp.model_energy(sp[mcc_loc],m[4],m[5],m[6])
            if (eng1 < 0) and (eng2 < 0):
                eng = -1
            elif (eng1 > 0) and (eng2 < 0):
                eng = -2
            elif (eng1 < 0) and (eng2 > 0):
                eng = -3
            else:
                eng = 1
            distance_angles.loc[mcc_loc,'Energy'] = eng
        else:
            temp_num = int(i[9:])
            distance_angles.loc[mcc_loc,i] = mnp.get_init_dih_ang(temp_chn,temp_num,dihe[temp_res][temp_ang])*180/np.pi
########################################################################################################################
def rot_dihedral(i,spc,mcc_loc,ang,distance_angles,terminal,m):
    spc_m = spc[mcc_loc].copy()
    mnp.dihedral_rotation_model(spc_m,i[8:9],int(i[9:]),i[0:3],i[4:7],dihe[i[0:3]][i[4:7]],terminal,ang)
    eng1 = mnp.model_energy(spc_m,m[0],m[1],m[2])
    eng2 = mnp.model_energy(spc_m,m[4],m[5],m[6])
    if (eng1 < 0) and (eng2 < 0):
        eng = -1
    elif (eng1 > 0) and (eng2 < 0):
        eng = -2
    elif (eng1 < 0) and (eng2 > 0):
        eng = -3
    else:
        eng = 1
    #if eng < 0:
    mcc_loc += 1
    spc_m.id = mcc_loc
    spc.add(spc_m)
    #distance_angles.loc[mcc_loc,i] = distance_angles.loc[(mcc_loc-1),i] + ang*180/np.pi
    for k in distance_angles.columns[1:]:
        if k == i:
            distance_angles.loc[mcc_loc,i] = distance_angles.loc[(mcc_loc-1),i] + ang*180/np.pi
        else:
            distance_angles.loc[mcc_loc,k] = distance_angles.loc[(mcc_loc-1),k]
    mnp.prep_dihedrals(spc,mcc_loc)
    # TODO: place distance metrics in parameters passed.
    d1 = mnp.get_vector_list(spc,mcc_loc,m[0],m[2],[m[3]])
    d2 = mnp.get_vector_list(spc,mcc_loc,m[4],m[6],[m[7]])
    distance_angles.loc[mcc_loc,'Distance'] = mnp.vector_lists_rmsd(d1,d2)
    distance_angles.loc[mcc_loc,'Energy'] = eng
    return mcc_loc
########################################################################################################################
# Now set all dihedral angles to 0 and output them
#def rot_dihedral_tree(i,spc,mcc_loc,ang,distance_angles,terminal):
#    print(mcc_loc)
#    if mcc_loc < 8:
#        rot_dihedral_tree(i,spc,mcc_loc+1,ang,distance_angles,terminal)
#        rot_dihedral(i,spc,mcc,ang,distance_angles,pd_loc)
########################################################################################################################
sp = pdb_parser.get_structure('insulin_bi_linker', struct_path)
params = CP.read_charmm_FF(charmmdir)
mnp = MRM.Molecular_Rigid_Manipulation(params)
mnp.prep_dihedrals(sp,0)
df_cols = ['Distance','Energy','LYS_psi_A6','LYS_ch1_A6','LYS_psi_B6','LYS_ch1_B6']
distance_angles = pd.DataFrame(columns=df_cols)
mcc_loc = 0
calculate_dih_angles(sp,mcc_loc,mnp,distance_angles,('A','LYS',6,'N','B','LYS',6,'N'))
#mcc_loc += 1
spc = sp.copy()
modes = ['sequencial','combinatorial','guided']
mode = modes[0]
if mode == 'sequencial':
    # Set Dihedrals to 0. Not necessary but good for reference.
    measure = ('A','LYS',2,'N','B','LYS',2,'N')
    for i in distance_angles.columns[2:]:
        mcc_loc = rot_dihedral(i,spc,mcc_loc,-1*mnp.get_init_dih_ang(i[8:9],int(i[9:]),dihe[i[0:3]][i[4:7]]),\
                               distance_angles,'NTERM',measure)
    for i in distance_angles.columns[2:]:
        for j in range(0,24):
            mcc_loc = rot_dihedral(i,spc,mcc_loc,15*np.pi/180,distance_angles,'NTERM',measure)
elif mode == 'combinatorial':
    # Set Dihedrals to 0. Not necessary but good for reference.
    measure = ('A','LYS',6,'N','B','LYS',6,'N')
    for i in distance_angles.columns[2:]:
        mcc_loc = rot_dihedral(i,spc,mcc_loc,-1*mnp.get_init_dih_ang(i[8:9],int(i[9:]),dihe[i[0:3]][i[4:7]]),\
                                distance_angles,'NTERM',measure)
    #rot_dihedral_tree('ASP_psi_A2',spc,mcc_loc+1,45*np.pi/180,distance_angles,terminal)
    for h in range(0,8):
        mcc_loc = rot_dihedral('LYS_psi_A6',spc,mcc_loc,45*np.pi/180,distance_angles,'NTERM',measure)
        for i in range(0,8):
            mcc_loc = rot_dihedral('LYS_psi_B6',spc,mcc_loc,45*np.pi/180,distance_angles,'NTERM',measure)
            for j in range(0,4):
                mcc_loc = rot_dihedral('LYS_ch1_A6',spc,mcc_loc,90*np.pi/180,distance_angles,'NTERM',measure)
                for j in range(0,4):
                    mcc_loc = rot_dihedral('LYS_ch1_B6',spc,mcc_loc,90*np.pi/180,distance_angles,'NTERM',measure)
elif mode == 'guided':
    # Set Dihedrals to 0. Not necessary but good for reference.
    measure = ('A','LYS',6,'N','B','LYS',6,'N')
    for i in distance_angles.columns[2:]:
        mcc_loc = rot_dihedral(i,spc,mcc_loc,-1*mnp.get_init_dih_ang(i[8:9],int(i[9:]),dihe[i[0:3]][i[4:7]]),\
                                distance_angles,'NTERM',measure)
    #rot_dihedral_tree('ASP_psi_A2',spc,mcc_loc+1,45*np.pi/180,distance_angles,terminal)
    for h in range(0,8):
        mcc_loc = rot_dihedral('LYS_psi_A6',spc,mcc_loc,45*np.pi/180,distance_angles,'NTERM',measure)
        for i in range(0,8):
            mcc_loc = rot_dihedral('LYS_psi_B6',spc,mcc_loc,45*np.pi/180,distance_angles,'NTERM',measure)
            for j in range(0,4):
                mcc_loc = rot_dihedral('LYS_ch1_A6',spc,mcc_loc,90*np.pi/180,distance_angles,'NTERM',measure)
                for j in range(0,4):
                    mcc_loc = rot_dihedral('LYS_ch1_B6',spc,mcc_loc,90*np.pi/180,distance_angles,'NTERM',measure)
    # Chain B found a nice conformation. Chain A need work.
    df_cols = ['Distance','Energy','GLY_phi_A7','LYS_psi_A6','LYS_ch1_A6']
    distance_angles = pd.DataFrame(columns=df_cols)
    measure = ('A','LYS',6,'N','B','LYS',6,'N')
    mcc_loc = 0
    calculate_dih_angles(sp,mcc_loc,mnp,distance_angles,('A','LYS',6,'N','B','LYS',6,'N'))
    #mcc_loc += 1
    spc = sp.copy()
    for i in distance_angles.columns[2:]:
        mcc_loc = rot_dihedral(i,spc,mcc_loc,-1*mnp.get_init_dih_ang(i[8:9],int(i[9:]),dihe[i[0:3]][i[4:7]]),\
                                distance_angles,'NTERM',measure)
    for h in range(0,4):
        mcc_loc = rot_dihedral('GLY_phi_A7',spc,mcc_loc,90*np.pi/180,distance_angles,'NTERM',measure)
        for i in range(0,4):
            mcc_loc = rot_dihedral('LYS_psi_A6',spc,mcc_loc,90*np.pi/180,distance_angles,'NTERM',measure)
            for j in range(0,3):
                mcc_loc = rot_dihedral('LYS_ch1_A6',spc,mcc_loc,120*np.pi/180,distance_angles,'NTERM',measure)
    # SET bot LYS 6 to desired values and continue search.
    df_cols = ['Distance','Energy','GLY_phi_A7','LYS_psi_A6','LYS_ch1_A6','LYS_phi_A6','ASP_psi_A5']
    distance_angles = pd.DataFrame(columns=df_cols)
    measure = ('A','LYS',6,'N','B','LYS',6,'N')
    mcc_loc = 0
    calculate_dih_angles(sp,mcc_loc,mnp,distance_angles,('A','LYS',6,'N','B','LYS',6,'N'))
    #mcc_loc += 1
    spc = sp.copy()
    for i in distance_angles.columns[2:]:
        mcc_loc = rot_dihedral(i,spc,mcc_loc,-1*mnp.get_init_dih_ang(i[8:9],int(i[9:]),dihe[i[0:3]][i[4:7]]),\
                                distance_angles,'NTERM',measure)
    mcc_loc = rot_dihedral('GLY_phi_A7',spc,mcc_loc,-90*np.pi/180,distance_angles,'NTERM',measure)
    mcc_loc = rot_dihedral('LYS_psi_A6',spc,mcc_loc,-90*np.pi/180,distance_angles,'NTERM',measure)
    mcc_loc = rot_dihedral('LYS_ch1_A6',spc,mcc_loc,120*np.pi/180,distance_angles,'NTERM',measure)
    mcc_loc = rot_dihedral('LYS_phi_B6',spc,mcc_loc,180*np.pi/180,distance_angles,'NTERM',measure)
    mcc_loc = rot_dihedral('LYS_psi_B6',spc,mcc_loc,180*np.pi/180,distance_angles,'NTERM',measure)
    mcc_loc = rot_dihedral('LYS_ch1_B6',spc,mcc_loc,-90*np.pi/180,distance_angles,'NTERM',measure)
    # Set Lys 6s and searc ASP 5
    df_cols = ['Distance','Energy','ASP_psi_A5','ASP_phi_A5','ASP_psi_B5','ASP_phi_B5']
    distance_angles = pd.DataFrame(columns=df_cols)
    measure = ('A','LYS',5,'N','B','LYS',5,'N')
    mcc_loc = 0
    calculate_dih_angles(sp,mcc_loc,mnp,distance_angles,('A','LYS',6,'N','B','LYS',6,'N'))
    #mcc_loc += 1
    spc = sp.copy()
    for i in distance_angles.columns[2:]:
        mcc_loc = rot_dihedral(i,spc,mcc_loc,-1*mnp.get_init_dih_ang(i[8:9],int(i[9:]),dihe[i[0:3]][i[4:7]]),\
                                distance_angles,'NTERM',measure)
    mcc_loc = rot_dihedral('GLY_phi_A7',spc,mcc_loc,-90*np.pi/180,distance_angles,'NTERM',measure)
    mcc_loc = rot_dihedral('LYS_psi_A6',spc,mcc_loc,-90*np.pi/180,distance_angles,'NTERM',measure)
    mcc_loc = rot_dihedral('LYS_ch1_A6',spc,mcc_loc,120*np.pi/180,distance_angles,'NTERM',measure)
    mcc_loc = rot_dihedral('LYS_phi_B6',spc,mcc_loc,180*np.pi/180,distance_angles,'NTERM',measure)
    mcc_loc = rot_dihedral('LYS_psi_B6',spc,mcc_loc,180*np.pi/180,distance_angles,'NTERM',measure)
    mcc_loc = rot_dihedral('LYS_ch1_B6',spc,mcc_loc,-90*np.pi/180,distance_angles,'NTERM',measure)
    for h in range(0,4):
        mcc_loc = rot_dihedral('ASP_psi_A5',spc,mcc_loc,90*np.pi/180,distance_angles,'NTERM',measure)
        for i in range(0,4):
            mcc_loc = rot_dihedral('ASP_psi_B5',spc,mcc_loc,90*np.pi/180,distance_angles,'NTERM',measure)
########################################################################################################################
pdb_out_filename = base_dir+'examples/Super_Structure/add_hydrogens/insln_lnk_ddddk_ab_1rr_6.pdb'
line = '{:6}{:>5} {:4}{:1}{:3} {:1}{:>4d}{:1}   {:>8.3f}{:>8.3f}{:>8.3f}{:>6.2f}{:>6.2f}          {:>2}{:2}'
# TODO: label_aaid shoould move to a utilities class
# TODO: check that label id still works for entities that have multiple chains
label_aaid = {1:'A',2:'B',3:'C',4:'D'}
lines = []
for g in spc.get_models():
    count = 1
    #self.get_missing_aa_DataFrame(g)
    # origianl atomic structures
    lines.append('MODEL      '+str(g.get_id()))
    for h in g.get_chains():
        for i in h.get_residues():
            for j in i.get_atom():
                #if g.get_id() == 0:
                lines.append(line.format('ATOM',str(count),j.get_id(),\
                '',i.get_resname(),h.get_id(),i.get_id()[1],'',j.get_coord()[0],\
                j.get_coord()[1],j.get_coord()[2],j.get_occupancy(),\
                j.get_bfactor(),j.get_name()[0],''))
                count += 1
    lines.append('ENDMDL')
outFile = open(pdb_out_filename, 'w')
for i in lines:
    outFile.write(i+'\n')
outFile.close()
#io = PDBIO()
#io.set_structure(spc)
#io.save(pdb_out_filename)

counter = 0
structure_id = 0
if terminal == 'NTERM':
    if 360 % angle_increment == 0:
        mc = 0
        d0 = mnpA.vector_lists_rmsd(mnpA.get_vector_list(sp,mc,'C',31,['C']),mnpA.get_vector_list(sp,mc,'E',link_A[1],['HN']))
        spc = sp.copy()
        mcc = 0
        psi = mnp.get_init_dih_ang(link_A[1],'N CA C +N')*180/np.pi
        phi = mnp.get_init_dih_ang(link_A[1],'-C N CA C')*180/np.pi
        for i in range(link_A[1],1,-1):
            angj = 0
            s1 = sp.copy()
            for j in range(angle_increment,360,angle_increment):
                mnp.dihedral_rotation(s1,mc,'E',i,'N CA C +N','NTERM',angle_increment*np.pi/180)
                d1 = mnp.vector_lists_rmsd(mnp.get_vector_list(s1,mc,'C',31,['C']),mnp.get_vector_list(s1,mc,'E',i,['HN']))
                if d1 < d0:
                    d0 = d1
                    angj = j
            mnp.dihedral_rotation(sp,mc,'E',i,'N CA C +N','NTERM',angj*np.pi/180)
            
            spc_m = sp[0].copy()
            spc_m.id = mcc + 1
            mcc += 1
            spc.add(spc_m)

            angk = 01
            s1 = sp.copy()
            for k in range(angle_increment,360,angle_increment):
                mnp.dihedral_rotation(s1,mc,'E',i,'-C N CA C','NTERM',angle_increment*np.pi/180)
                d1 = mnp.vector_lists_rmsd(mnp.get_vector_list(s1,mc,'C',31,['C']),mnp.get_vector_list(s1,mc,'E',i,['HN']))
                if d1 < d0:
                    d0 = d1
                    angk = k
            mnp.dihedral_rotation(sp,mc,'E',i,'-C N CA C','NTERM',angk*np.pi/180)
            d1 = mnp.vector_lists_rmsd(mnp.get_vector_list(s1,mc,'C',31,['C']),mnp.get_vector_list(s1,mc,'E',i,['HN'])) 
            psi = mnp.get_init_dih_ang(i,'N CA C +N')*180/np.pi
            phi = mnp.get_init_dih_ang(i,'-C N CA C')*180/np.pi
            distance_angle.loc[pd_loc] = [1,i,psi,phi,d0,d1]
            pd_loc += 1
            
            spc_m = sp[0].copy()
            spc_m.id = mcc + 1
            mcc += 1
            spc.add(spc_m)
    else:
        print("ERROR: angle increment must be multiple of 360.")
elif link_A[2] == 'CTERM':
    pass

pdb_out_filename = '/home/noel/Projects/Protein_design/Insulin/Struct_Prep/pdbs/link1.pdb'
io = PDBIO()
io.set_structure(spc)
io.save(pdb_out_filename)
