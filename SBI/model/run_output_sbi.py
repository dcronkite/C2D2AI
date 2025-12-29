# * ESPRESSO SBI Pt-level output
# * Process neuroimaging reports to classify a patient's SBI and WMD status
# * @author Sunyang Fu
# fail when directly run the code 
# error message: Failed to read a resource from used_resources.txt.
# use absolute location to read rule files 
# still fail with the same erroe message--- yichen 
import csv
import re
from pathlib import Path


def rad_parser(line):
    line = str(line.encode('utf-8'))
    line = line.replace('[', '')
    line = line.replace(']', '')
    line = line.replace("'", '')
    line = line.replace('}', '')

    return '\n'.join(line[121:].split(r'\par'))


def sent_parser(line):
    return re.sub(r'[^a-z0-9]+', ' ', f' {line} '.lower())


def read_txt_to_lines(indir):
    with open(indir) as fh:
        return fh.read().split('\n')


def apply_exclusion_wmd(sent, filehandle):
    return _apply(sent, filehandle, True)


def apply_positive_screen(sent, filehandle):
    return _apply(sent, filehandle, True)


def apply_negative_screen(sent, filehandle):
    return _apply(sent, filehandle, False)


def _apply(sent, filehandle, if_present_return):
    for k in read_txt_to_lines(filehandle):
        k = f' {k} '
        sent = ' ' + sent.lower().replace('.', ' ')
        if k in sent:
            return if_present_return
    return not if_present_return


def apply_sbi_location(sent, filehandle):
    outnorm1, outnorm2 = '', ''
    sent = sent_parser(sent)
    for k in read_txt_to_lines(filehandle):
        term, norm1, norm2, *_ = k.split('\t')
        term = f' {term} '
        # print(term, sent)
        if term in sent:
            if norm1 != 'null':
                outnorm1 = norm1
            if norm2 != 'null':
                outnorm2 = norm2
            # print(term, outnorm1, outnorm2)
    return outnorm1, outnorm2


def apply_wmd_gd(sent, file1, file2):
    secondary_list = [' multifocal ', ' several ']
    outgd = 0
    priority = 1
    sent = sent.split('\"')[1]
    for k in read_txt_to_lines(file1):
        term = k.split('\t')[0]
        norm1 = int(k.split('\t')[1])
        term = ' ' + term + ' '
        sent = sent_parser(sent)
        notexc = True
        for e in read_txt_to_lines(file2):
            if term.strip() == e:
                notexc = False
                # print (notexc, [term], [sent])
        if notexc and term in sent:
            # print(term, sent)
            if term in secondary_list and outgd == 0:
                outgd = norm1
            elif term not in secondary_list:
                outgd = norm1
    # print(outgd, sent)
    return outgd


def run_eval_sbi(indir: Path, outdir: Path):
    file_output = outdir / 'patient_level.csv'
    # get the resources directory
    curdir = Path(__file__).parent.absolute()
    resdir = curdir / '..'  # SBI/
    regex_dir = resdir / 'regexp'
    norm_dir = resdir / 'norm'
    file_exclusion_wmd = regex_dir / 'resources_regexp_reWMDCXEXL.txt'
    file_positive_screen = regex_dir / 'resources_regexp_reSBIAlone.txt'
    file_negative_screen = regex_dir / 'resources_regexp_reSBICXEXL.txt'
    file_sbi_location = regex_dir / 'resources_regexp_reINFLocation.txt'
    file_wmd_gd1 = norm_dir / 'resources_norm_normWMDGD.txt'
    file_wmd_gd2 = regex_dir / 'resources_regexp_reWMDDGEXL.txt'

    outdir.mkdir(exist_ok=True)

    with open(file_output, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='|')
        for d in indir.glob('*.ann'):
            WMD_GD_T, temp_priority = 0, 0
            SBI_STATUS, WMD_STATUS, WMD_GD = '', '', ''
            SBI_STATUS_LIST = []
            SBI_LOCATION1 = []
            SBI_L1, SBI_L2 = '', ''
            with open(d) as csvfile:
                for row in csv.reader(csvfile, delimiter='\t'):
                    certainty = row[6]
                    status = row[7]
                    exp = row[8]
                    norm = row[9]
                    is_remove = 'REMOVE' in norm
                    sent = row[-1].lower()
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
                    if 'Positive' in certainty and not any(neg in sent for neg in negations):
                        if ('NONACUTE' in norm or 'INF_GENERAL' in norm or 'ACUTE' in norm) and (
                                'POSSIBLE' not in norm):
                            ns = apply_negative_screen(sent, file_negative_screen)
                            if ns:
                                SBI_STATUS_LIST += ['SBI_FOUND']
                                SBI_L1, SBI_L2 = apply_sbi_location(sent, file_sbi_location)
                                SBI_LOCATION1 += [SBI_L1]

                            # else:
                            #   SBI_STATUS_LIST += ['SBI_INDETERMINATE']
                    if 'Negated' not in certainty:
                        if 'WMD_WHITE' in norm or 'WMD_LEUK' in norm or 'WMD' in norm or 'WMD_SV' in norm:
                            exl = apply_exclusion_wmd(sent, file_exclusion_wmd)
                            if not exl and not is_remove:
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

            writer.writerow([d.name, SBI_STATUS, SBI_L1, SBI_L2, WMD_STATUS, WMD_GD])


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Process neuroimaging reports to classify SBI and WMD status')
    parser.add_argument('input_dir', type=Path, help='Input directory containing .ann files')
    parser.add_argument('output_dir', type=Path, help='Output directory for patient level results')

    args = parser.parse_args()
    run_eval_sbi(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
