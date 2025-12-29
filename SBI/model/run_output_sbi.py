# * ESPRESSO SBI Pt-level output
# * Process neuroimaging reports to classify a patient's SBI and WMD status
# * @author Sunyang Fu
# fail when directly run the code 
# error message: Failed to read a resource from used_resources.txt.
# use absolute location to read rule files 
# still fail with the same erroe message--- yichen 
import csv
import sys
import re
import os
import string
import glob

def rad_parser(line):
    line = str(line.encode('utf-8'))
    line = line.replace('[', '')
    line = line.replace(']', '')
    line = line.replace('\'', '')
    line = line.replace('}', '')
    # line = line.replace('', '')
    line = line[121:]
    line = line.split(r'\par')
    line_str = ''
    for m in line:
        line_str += m + '\n' 
    line = line_str
    return line

def sent_parser(line):
    line = ' '+line+' '
    line = re.sub(r"[^A-Za-z0-9]", " ", line)
    line = line.replace('\t', ' ')
    line = re.sub(' +', ' ', line)
    return line.lower()


def read_txt(indir):
    f = open(indir,'r')
    txt = f.read()
    f.close()
    l = txt.split('\n')
    return l

def read_file_list(indir, deli):
    opt_notes = []
    #Removed deprecated 'U' flag from open (KZ 2024-11-13)
    with open(indir, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=deli)
        for row in spamreader:
            opt_notes += [row]
    return opt_notes

def apply_exclusion_wmd(sent, filehandle):
    # elist = read_txt('/reev/data/proj_SBI/ESPRESSO-2023/SBI/regexp/resources_regexp_reWMDCXEXL.txt')
    # curdir = os.getcwd()
    # filehandle = curdir+'/SBI/regexp/resources_regexp_reWMDCXEXL.txt'
    elist = read_txt(filehandle)
    for k in elist:
        k = ' '+k+' '
        sent = ' '+sent.lower().replace('.', ' ')
        if k in sent:
            return True
    return False

def apply_positive_screen(sent, filehandle):
    # elist = read_txt('/reev/data/proj_SBI/ESPRESSO-2023/SBI/regexp/resources_regexp_reSBIAlone.txt')
    elist = read_txt(filehandle)
    for k in elist:
        k = ' '+k+' '
        sent = ' '+sent.lower().replace('.', ' ')
        if k in sent:
            return True
    return False    

def apply_negative_screen(sent, filehandle):
    # elist = read_txt('/reev/data/proj_SBI/ESPRESSO-2023/SBI/regexp/resources_regexp_reSBICXEXL.txt')
    elist = read_txt(filehandle)
    for k in elist:
        k = ' '+k+' '
        sent = ' '+sent.lower().replace('.', ' ')
        if k in sent:
            return False
    return True

def get_remove(l, deli):
    r = {}
    for d in l:
        fname = d.split(deli)[-1]
        SBI_STATUS, WMD_STATUS, WMD_GD = '','',''
        ann_list = read_file_list(d,'\t')
        for row in ann_list:
            key = fname+row[-2]
            norm = row[9]
            if 'REMOVE' in norm:
                r[key] = 1
    return r
        
def apply_sbi_location(sent, filehandle):
    # elist = read_txt('/reev/data/proj_SBI/ESPRESSO-2023/SBI/regexp/resources_regexp_reINFLocation.txt')
    elist = read_txt(filehandle)
    outnorm1,outnorm2 = '',''
    for k in elist:
        term = k.split('\t')[0]
        norm1 = k.split('\t')[1]
        norm2 = k.split('\t')[2]
        term = ' '+term+' '
        sent = sent_parser(sent)
        # print(term, sent)
        if term in sent:
            if norm1 != 'null':
                outnorm1 = norm1
            if norm2 != 'null':
                outnorm2 = norm2
            # print(term, outnorm1, outnorm2)
    return outnorm1, outnorm2

def apply_wmd_gd(sent, file1, file2):
    # elist = read_txt('/reev/data/proj_SBI/ESPRESSO-2023/SBI/norm/resources_norm_normWMDGD.txt')
    # exc = read_txt('/reev/data/proj_SBI/ESPRESSO-2023/SBI/regexp/resources_regexp_reWMDDGEXL.txt')
    elist = read_txt(file1)
    exc = read_txt(file2)
    secondary_list = [' multifocal ', ' several ']
    outgd = 0
    priority = 1
    sent = sent.split('\"')[1]
    for k in elist:
        term = k.split('\t')[0]
        norm1 = int(k.split('\t')[1])
        term = ' '+term+' '
        sent = sent_parser(sent)
        notexc = True       
        for e in exc:
            if term.strip() == e:
                notexc = False  
        # print (notexc, [term], [sent])
        if notexc and term in sent:
            # print(term, sent)
            if term in secondary_list and outgd ==0:
                outgd = norm1
            elif term not in secondary_list:
                outgd = norm1
    # print(outgd, sent)
    return outgd


def run_eval_sbi(indir, outdir, sys):
    if sys == '0':
        deli = '/'
        curdir = os.getcwd()
        file_output = curdir+'/output/summary/patient_level.csv'
        file_exclusion_wmd = curdir+'/SBI/regexp/resources_regexp_reWMDCXEXL.txt'
        file_positive_screen = curdir+'/SBI/regexp/resources_regexp_reSBIAlone.txt'
        file_negative_screen = curdir+'/SBI/regexp/resources_regexp_reSBICXEXL.txt'
        file_sbi_location = curdir+'/SBI/regexp/resources_regexp_reINFLocation.txt'
        file_wmd_gd1 = curdir+'/SBI/norm/resources_norm_normWMDGD.txt'
        file_wmd_gd2 = curdir+'/SBI/regexp/resources_regexp_reWMDDGEXL.txt'
    else:
        deli = '\\'
        curdir = os.getcwd()
        file_output = curdir+'\\output\\summary\\patient_level.csv'
        file_exclusion_wmd = curdir+'\\SBI\\regexp\\resources_regexp_reWMDCXEXL.txt'
        file_positive_screen = curdir+'\\SBI\\regexp\\resources_regexp_reSBIAlone.txt'
        file_negative_screen = curdir+'\\SBI\\regexp\\resources_regexp_reSBICXEXL.txt'
        file_sbi_location = curdir+'\\SBI\\regexp\\resources_regexp_reINFLocation.txt'
        file_wmd_gd1 = curdir+'\\SBI\\norm\\resources_norm_normWMDGD.txt'
        file_wmd_gd2 = curdir+'\\SBI\\regexp\\resources_regexp_reWMDDGEXL.txt'
    dir_list = indir+deli+'*.ann'
    l = glob.glob(dir_list)
    output = []
    rm = get_remove(l, deli)
    #make dir outdir if not exists
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # with open(file_output, 'w') as csvfile:
    with open(outdir+deli+'patient_level.csv', 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter='|')
        # Rest of the code...
 
    # with open(file_output, 'w') as csvfile:
    with open(outdir+deli+'patient_level.csv', 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter='|')
        for d in l:
            fname = d.split(deli)[-1]
            WMD_GD_T, temp_priority = 0, 0
            SBI_STATUS, WMD_STATUS, WMD_GD = '','',''
            SBI_STATUS_LIST = []
            ann_list = read_file_list(d,'\t')
            SBI_LOCATION1 = []
            SBI_L1, SBI_L2 = '',''
            for row in ann_list:
                rm_term = fname+row[-2]
                certainty = row[6]
                status = row[7]
                exp = row[8]
                norm = row[9]
                sent = row[-1].lower()
                key = fname+row[-2]
                double_eval = False
                indeterminate_status = False
                indeterminates = [
                    'may represent chronic lacunar infarcts',
                    'which may represent a chronic lacunar infarction', 
                    'which may represent prior lacunar infarct',
                    'may represent a lacunar infarct',
                    'likely small perivascular space or old lacunar infarct', 
                    'nonspecific but likely due to chronic small vessel ischemia', 
                    'probably a prominent perivascular space or remote lacunar infarction',
                    'early acute infarction not excluded',
                    'perhaps due to an old infarct',
                    'possibly an old small infarct',
                    'may reflect gliosis from remote cortical infarcts',
                    'findings consistent with chronic small vessel ischemic changes of the periventricular white matter',
                    'early acute infarction not excluded',
                    'moderate to severe sequela of chronic small vessel ischemic changes',
                    'considerations vascular lesions such as capillary telangiectasia or sequela of old hemorrhagicum infarct',
                    'likely reflect small lacunes and appears old'
                    ]
                negations = [
                    'no area of increased or decreased attenuation to suggest hemorrhage, infarct',
                    'no evidence of acute infarct',
                    'infarcts : none',
                    'infarct: none',
                    'no restricted diffusion'
                    ]
                negations += indeterminates
                negations = [n.lower() for n in negations]
                # if ('Negation' not in certainty) and 'Present' in status and 'Patient' in exp:
                #   if'INF_INDETERMINATE' in norm:
                #       SBI_STATUS_LIST += ['SBI_INDETERMINATE']
                #       indeterminate_status = True
                # if ('Possible' in certainty) and 'Present' in status and 'Patient' in exp:
                #   if ('NONACUTE' in norm or 'INF_GENERAL' in norm or 'ACUTE' in norm):
                #       SBI_STATUS_LIST += ['SBI_INDETERMINATE']
                #       indeterminate_status = True
                # if ('Hypothetical' in certainty) and 'Present' in status and 'Patient' in exp:
                #   if ('NONACUTE' in norm or 'INF_GENERAL' in norm or 'ACUTE' in norm):
                #       SBI_STATUS_LIST += ['SBI_INDETERMINATE']
                #       indeterminate_status = True
                if indeterminate_status and not any(neg in sent for neg in negations):
                    ps = apply_positive_screen(sent, file_positive_screen)
                    if ps:
                        SBI_STATUS_LIST += ['SBI_FOUND']
                if ('Positive' in certainty) and not any(neg in sent for neg in negations):
                    if ('NONACUTE' in norm or 'INF_GENERAL' in norm or 'ACUTE' in norm) and ('POSSIBLE' not in norm):
                        ns = apply_negative_screen(sent, file_negative_screen)
                        if ns:
                            SBI_STATUS_LIST += ['SBI_FOUND']
                            SBI_L1, SBI_L2 = apply_sbi_location(sent, file_sbi_location)
                            SBI_LOCATION1 += [SBI_L1]

                        # else:
                        #   SBI_STATUS_LIST += ['SBI_INDETERMINATE']
                if ('Negated' not in certainty):                            
                    if 'WMD_WHITE' in norm or 'WMD_LEUK' in norm or 'WMD' in norm or 'WMD_SV' in norm:
                        exl = apply_exclusion_wmd(sent, file_exclusion_wmd)
                        if not exl and rm_term not in rm:
                            WMD_STATUS = 'WMD_FOUND'
                            temp_priority = apply_wmd_gd(sent, file_wmd_gd1, file_wmd_gd2)
                            if temp_priority > WMD_GD_T:
                                WMD_GD_T = temp_priority
                
                # Negate any mention of "No evidence of acute infarct"

                # if SBI_STATUS_LIST!= [] and SBI_STATUS_LIST[-1] == 'SBI_FOUND':


            if 'SBI_FOUND' in SBI_STATUS_LIST:
                SBI_STATUS = 'SBI_FOUND'
                if 'cortical_juxtacortical' in SBI_LOCATION1 and 'lacunar_subcortical' in SBI_LOCATION1:
                    SBI_L1 = 'both'
                elif 'cortical_juxtacortical' in SBI_LOCATION1:
                    SBI_L1 = 'cortical_juxtacortical'
                elif 'lacunar_subcortical' in SBI_LOCATION1:
                    SBI_L1 = 'lacunar_subcortical'
                else:
                    SBI_L1 = ''
                
            if WMD_GD_T == 3:
                WMD_GD = 'SEVERE'
            elif WMD_GD_T == 2:
                WMD_GD = 'MODERATE'     
            elif WMD_GD_T == 1:
                WMD_GD = 'MILD'     
            elif WMD_GD_T == 0:
                WMD_GD = ''

            spamwriter.writerow([fname, SBI_STATUS, SBI_L1, SBI_L2, WMD_STATUS, WMD_GD])

def main():
    args = sys.argv[1:]
    run_eval_sbi(args[0], args[1], args[2])

if __name__== "__main__":
    main()





