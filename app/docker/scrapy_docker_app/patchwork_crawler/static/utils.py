import re
import requests
import json
import dateutil
from html.parser import HTMLParser
from dateutil import parser


class HTMLFilter(HTMLParser):
    text = ""

    def handle_data(self, data):
        self.text += data


class MailingListBase():
    def get_project_original_id(self, response_url):
        project_mapping = {
            "https://ffmpeg.org/pipermail/ffmpeg-devel/": "ffmpeg-project-1",
            "https://lists.buildroot.org/pipermail/buildroot/": "ozlabs-project-27",
            "https://gcc.gnu.org/pipermail/gcc-patches/": "ozlabs-project-17",
            "https://lists.denx.de/pipermail/u-boot/": "ozlabs-project-18",
            "https://lists.infradead.org/pipermail/kvm-riscv/": "ozlabs-project-70",
            "https://lists.infradead.org/pipermail/linux-snps-arc/": "ozlabs-project-48",
            "https://lists.infradead.org/pipermail/lede-dev/": "ozlabs-project-54",
            "https://lists.infradead.org/pipermail/linux-um/": "ozlabs-project-60",
            "https://lists.infradead.org/pipermail/opensbi/": "ozlabs-project-67",
            "https://lists.infradead.org/pipermail/linux-mtd/": "ozlabs-project-3",
            "https://lists.infradead.org/pipermail/hostap/": "ozlabs-project-22",
            "https://lists.linux.it/pipermail/ltp/": "ozlabs-project-59",
            "https://lists.openwrt.org/pipermail/openwrt-devel/": "ozlabs-project-45",
            "https://lists.ozlabs.org/pipermail/skiboot/": "ozlabs-project-44",
            "https://lists.ozlabs.org/pipermail/slof/": "ozlabs-project-50",
            "https://lists.ozlabs.org/pipermail/snowpatch/": "ozlabs-project-51",
            "https://lists.ozlabs.org/pipermail/petitboot/": "ozlabs-project-53",
            "https://lists.ozlabs.org/pipermail/openbmc/": "ozlabs-project-56",
            "https://lists.ozlabs.org/pipermail/linux-aspeed/": "ozlabs-project-57",
            "https://lists.ozlabs.org/pipermail/pdbg/": "ozlabs-project-61",
            "https://lists.ozlabs.org/pipermail/skiboot-stable/": "ozlabs-project-62",
            "https://lists.ozlabs.org/pipermail/linux-fsi/": "ozlabs-project-65",
            "https://lists.ozlabs.org/pipermail/yaboot-devel/": "ozlabs-project-11",
            "https://lists.ozlabs.org/pipermail/patchwork/": "ozlabs-project-16",
            "https://lists.ozlabs.org/pipermail/cbe-oss-dev/": "ozlabs-project-1",
            "https://lists.ozlabs.org/pipermail/linuxppc-dev/": "ozlabs-project-2",
            "https://lists.ozlabs.org/pipermail/linuxppc-embedded/": "ozlabs-project-5",
            "https://lists.ubuntu.com/archives/kernel-team/": "ozlabs-project-15",
            "https://lists.ubuntu.com/archives/fwts-devel/": "ozlabs-project-24",
            "https://lists.nongnu.org/archive/html/qemu-ppc/": "ozlabs-project-69",
            "https://mail.openvswitch.org/pipermail/ovs-dev/": "ozlabs-project-68",
            "https://oss.oracle.com/pipermail/fedfs-utils-devel/": "ozlabs-project-20",
            "https://lists.osuosl.org/pipermail/intel-wired-lan/": "ozlabs-project-46",
            "https://sourceware.org/pipermail/libc-alpha/": "ozlabs-project-41",
            "https://sourceware.org/pipermail/crossgcc/": "ozlabs-project-33",
            "https://lists.uclibc.org/pipermail/uclibc/": "ozlabs-project-36",
        }

        for base_url, org_id in project_mapping.items():
            if base_url in response_url:
                return org_id

        return None

    def is_patch_related(self, email_title, email_content):
        is_git_commit = re.findall(r'git commit', email_title, re.IGNORECASE)
        title_keywords = re.findall(
            r'\[.*?patch.*?\]|\d+/\d+|v\d+', email_title, re.IGNORECASE)
        content_keywords = re.findall(
            r'diff --git', email_content, re.IGNORECASE)

        if (title_keywords or content_keywords) and not is_git_commit:
            return True
        else:
            return False

    def convert_datetime(self, datetime_string):
        timezone_str = '''-12 Y
        -11 X NUT SST
        -10 W CKT HAST HST SDT TAHT TKT
        -9 V AKST GAMT GIT HADT HNY
        -8 U AKDT CIST HAY HNP PST PT
        -7 T HAP HNR MST PDT
        -6 S CST EAST GALT HAR HNC MDT
        -5 R CDT COT EASST ECT EST ET HAC HNE PET
        -4 Q AST BOT CLT COST EDT FKT GYT HAE HNA PYT
        -3 P ADT ART BRT CLST FKST GFT HAA PMST PYST SRT UYT WGT
        -2 O BRST FNT PMDT UYST WGST
        -1 N AZOT CVT EGT
        0 Z EGST GMT UTC WET WT
        1 A BST CET DFT IST WAT WEDT WEST
        2 B CAT CEDT CEST EET SAST WAST
        3 C EAT EEDT EEST FET IDT MSK TRT
        4 D AMT AZT GET GST KUYT MSD MUT RET SAMT SCT
        5 E AMST AQTT AZST HMT MAWT MVT PKT TFT TJT TMT UZT YEKT
        6 F ALMT BIOT BTT IOT KGT NOVT OMST YEKST
        7 G CXT DAVT HOVT ICT KRAT NOVST OMSST THA WIB
        8 H ACT AWST BDT BNT CAST HKT IRKT KRAST MYT PHT SGT ULAT WITA WST
        9 I AWDT IRKST JST KST PWT TLT WDT WIT YAKT
        10 K AEST CHST PGT VLAT YAKST YAPT
        11 L AEDT LHDT MAGT NCT PONT SBT VLAST VUT
        12 M ANAST ANAT FJT GILT MAGST MHT NZST PETST PETT TVT WFT
        13 FJST NZDT
        11.5 NFT
        10.5 ACDT LHST
        9.5 ACST
        6.5 CCT MMT
        5.75 NPT
        5.5 SLT
        4.5 AFT IRDT
        3.5 IRST
        -2.5 HAT NDT
        -3.5 HNT NST NT
        -4.5 HLV VET
        -9.5 MART MIT'''

        timezone_dict = {}
        for timezone_descr in map(str.split, timezone_str.split('\n')):
            timezone_offset = int(float(timezone_descr[0]) * 3600)
            for timezone_abbr in timezone_descr[1:]:
                timezone_dict[timezone_abbr] = timezone_offset

        org_time = parser.parse(datetime_string, tzinfos=timezone_dict)
        utc_time = org_time.astimezone(dateutil.tz.tzutc())

        return utc_time


class PatchworkCrawlerBase():
    def get_page_json(self, res):
        raw_data = res.xpath('//*[@id="content"]/div[2]/div[4]/pre').get()
        raw_string = re.sub(r'<span.*</span>', '', ' '.join(raw_data.split()))

        html_filter = HTMLFilter()
        html_filter.feed(raw_string)
        json_string = html_filter.text

        # get a single series json
        json_data = json.loads(json_string)

        return json_data

    def get_request(self, url):
        counter = 0
        while counter <= 10:
            try:
                json_data = requests.get(url, timeout=20).json()
                return json_data
            except (requests.exceptions.JSONDecodeError, json.decoder.JSONDecodeError) as e:
                print(f"{url}: json decoder error")
                return None
            except Exception as e:
                print(f"{url}: other errors; counter: {counter}")
                print(e)
                counter += 1

        return None
