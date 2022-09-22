import scrapy, re
from gc import callbacks
from urllib.parse import unquote
from ..items import *
from ..static.utils import HTMLFilter, MailingListBase

class MailingListFormat1Spider(scrapy.Spider):

    name = 'mailing_list_format1'

    custom_settings = {
        'ITEM_PIPELINES': {},
        'HTTPERROR_ALLOWED_CODES': [404],
        'FEEDS': {
            './retrieved_data/mailing_list/mailinglist_format1_%(batch_id)d.jl': {
                'format': 'jsonlines',
                'overwrite': True
            }
        },
        'FEED_EXPORT_BATCH_ITEM_COUNT': 1000000
    }

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.base_func = MailingListBase()

        self.start_urls = [
            "https://ffmpeg.org/pipermail/ffmpeg-devel/",
            "https://lists.buildroot.org/pipermail/buildroot/",
            "https://gcc.gnu.org/pipermail/gcc-patches/",
            "https://lists.denx.de/pipermail/u-boot/",
            "https://lists.infradead.org/pipermail/kvm-riscv/",
            "https://lists.infradead.org/pipermail/linux-snps-arc/",
            "https://lists.infradead.org/pipermail/lede-dev/",
            "https://lists.infradead.org/pipermail/linux-um/",
            "https://lists.infradead.org/pipermail/opensbi/",
            "https://lists.infradead.org/pipermail/linux-mtd/",
            "https://lists.infradead.org/pipermail/hostap/",
            "https://lists.linux.it/pipermail/ltp/",
            "https://lists.openwrt.org/pipermail/openwrt-devel/",
            "https://lists.ozlabs.org/pipermail/skiboot/",
            "https://lists.ozlabs.org/pipermail/slof/",
            "https://lists.ozlabs.org/pipermail/snowpatch/",
            "https://lists.ozlabs.org/pipermail/petitboot/",
            "https://lists.ozlabs.org/pipermail/openbmc/",
            "https://lists.ozlabs.org/pipermail/linux-aspeed/",
            "https://lists.ozlabs.org/pipermail/pdbg/",
            "https://lists.ozlabs.org/pipermail/skiboot-stable/",
            "https://lists.ozlabs.org/pipermail/linux-fsi/",
            "https://lists.ozlabs.org/pipermail/yaboot-devel/",
            "https://lists.ozlabs.org/pipermail/patchwork/",
            "https://lists.ozlabs.org/pipermail/cbe-oss-dev/",
            "https://lists.ozlabs.org/pipermail/linuxppc-dev/",
            "https://lists.ozlabs.org/pipermail/linuxppc-embedded/",
            "https://lists.ubuntu.com/archives/kernel-team/",
            "https://lists.ubuntu.com/archives/fwts-devel/",
            "https://lists.nongnu.org/archive/html/qemu-ppc/",
            "https://mail.openvswitch.org/pipermail/ovs-dev/",
            "https://oss.oracle.com/pipermail/fedfs-utils-devel/",
            "https://lists.osuosl.org/pipermail/intel-wired-lan/",
            "https://sourceware.org/pipermail/libc-alpha/",
            "https://sourceware.org/pipermail/crossgcc/",
            "https://lists.uclibc.org/pipermail/uclibc/",
        ]


    def parse(self, response):
        for subject_href in response.xpath("//a[contains(text(), 'Subject')]/@href").getall()[:1]:
            
            yield response.follow(subject_href, callback=self.parse_subject)


    def parse_subject(self, response):
        email_list_sel = response.xpath("(//ul)[2]")

        # traverse emails in current subject page
        for email in email_list_sel.xpath("./li")[:5]:

            email_href = email.xpath("./a[@href]/@href").get()
            yield response.follow(email_href, callback=self.parse_email)


    def parse_email(self, response):
        
        email_subject = response.xpath("//h1/text()").get()
        # email_full_content = html.unescape(re.sub(r'</*a.*?>|</*pre>', '', response.xpath("//pre").get()))
        email_raw_content = response.xpath("//pre").get()

        # if the email subject contain the word "PATCH", then consider it related to patch submission and discussion
        # few cases exists where some emails related to patch submission do not have the word "PATCH" in their titles
        if self.base_func.is_patch_related(email_subject, email_raw_content):
            
            html_filter = HTMLFilter()
            html_filter.feed(email_raw_content)
            email_full_content = html_filter.text

            extra_info = response.xpath("//body/a/@href").get()

            decoded_info = unquote(extra_info)
            email_msg_id = re.search(r'In-Reply-To=(<.*?>)', decoded_info).group(1)
            email_date = self.base_func.convert_datetime(response.xpath("//body/i/text()").get())
            sender_name = response.xpath("//body/b/text()").get()
            web_url = response._url
            project_original_id = self.base_func.get_project_original_id(web_url)

            mailing_list_item = MailingListItem(
                msg_id = email_msg_id,
                subject = email_subject,
                content = email_full_content,
                date = email_date,
                sender_name = sender_name,
                web_url = web_url,
                project_original_id = project_original_id
            )

            yield mailing_list_item