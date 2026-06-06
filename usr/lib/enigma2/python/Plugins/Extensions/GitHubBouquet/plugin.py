# -*- coding: utf-8 -*-
import os
import urllib.request
import urllib.parse
import gzip  # 引入原生解压利器
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox

# ✨【核心重构】：引入本地翻译钩子
from . import _

# 引入 Config 组件来实现复选框列表和数据持久化保存
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSelection, getConfigListEntry, ConfigYesNo

try:
    from enigma import eDVBDB
except ImportError:
    pass

# ==================== 🛠️ 配置区（完全对齐你的 Shell 脚本） 🛠️ ====================
ROOT_FOLDER_NAME = "HSCK-motorcycles"

USER = "mathlabroom"
REPO = "huangseck-m3u8"
BRANCH = "main"          
REMOTE_DIR = "E2_Bouquets"
LOCAL_DIR = "/etc/enigma2"
CONFIG_FILE = "/etc/enigma2/github_bouquet_checkbox.conf"  # 勾选记忆文件
SIZE_FILE = "/etc/enigma2/github_bouquet_sizes.conf"       # 文件大小账本路径

# 💡 注意：前两项保持原样（用于内部逻辑与远程文件名匹配），我们只在 UI 层通过 _() 翻译其显示名称
BOUQUET_LIST = [
    ("CK - Domestic Series", "国产系列", REPO),
    ("CK - Uncensored Cavalry", "骑兵破解", REPO),
    ("CK - Japan Uncensored", "日本无码", REPO),
    ("CK - Japan Censored", "日本有码", REPO),
    ("CK - Uncensored Chinese Subtitles", "无码中文字幕", REPO),
    ("CK - Censored Chinese Subtitles", "有码中文字幕", REPO),
    ("CK - US/Europe HD", "欧美高清", REPO),
    ("CK - Anime", "动漫", REPO),
    ("MT - Movie Ethics", "三级伦理", "motorcycles"),
    ("MT - Chinese Subtitles", "中文字幕", "motorcycles"),
    ("MT - Anime Premium", "动漫精品", "motorcycles"),
    ("MT - Domestic Amateur", "国产自拍", "motorcycles"),
    ("MT - Hardcore/Taboo", "强奸乱伦", "motorcycles"),
    ("MT - Uncensored Video", "无码视频", "motorcycles"),
    ("MT - Japan Adult Video", "日本AV", "motorcycles"),
    ("MT - Censored Video", "有码视频", "motorcycles"),
    ("MT - US/Europe Premium", "欧美极品", "motorcycles"),
    ("MT - LGBT/Gay/Lesbian", "男同女同", "motorcycles"),
    ("MT - Heavy Taste", "重口味", "motorcycles")
]
# =======================================================================

class GitHubBouquetNestedScreen(Screen, ConfigListScreen):
    # 💡 皮肤里的 title 属性我们通过代码自适应动态赋予
    skin = """
        <screen name="GitHubBouquetNestedScreen" position="center,center" size="850,550" title="">
            <widget name="title_label" position="40,20" size="770,35" font="Regular;24" halign="left" transparent="1" foregroundColor="#00ffffff" />
            <widget name="config" position="40,75" size="770,364" itemHeight="52" scrollbarMode="showOnDemand" transparent="0" />
            <eLabel backgroundColor="#00444444" position="40,455" size="770,2" />
            
            <eLabel position="50,475" size="160,36" backgroundColor="#00ff2222" />
            <widget name="key_red" position="50,475" size="160,36" font="Regular;20" halign="center" valign="center" foregroundColor="#00ffffff" transparent="1" zPosition="1" />
            
            <eLabel position="240,475" size="160,36" backgroundColor="#0022ff22" />
            <widget name="key_green" position="240,475" size="160,36" font="Regular;20" halign="center" valign="center" foregroundColor="#00ffffff" transparent="1" zPosition="1" />
            
            <widget name="status" position="420,473" size="380,40" font="Regular;18" halign="right" valign="center" foregroundColor="#00aaaaaa" transparent="1" />
        </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        
        # ✨【国际化重构】：界面全部由英文骨架承载，自动对齐本地语言包
        self.setTitle(_("GitHub Bouquet Nested Downloader"))
        self["title_label"] = Label(_("Use Left/Right keys to select categories to update:"))
        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("Sync Selected"))
        self["status"] = Label(_("Press [Green] to smartly compare and sync"))
        
        saved_choices = self.load_saved_config()
        self.local_sizes = self.load_local_sizes()  # 加载本地大小记录
        
        self.checkbox_configs = {}
        self.list = []
        
        for idx, item in enumerate(BOUQUET_LIST):
            default_val = saved_choices.get(item[1], True)
            cfg_item = ConfigYesNo(default=default_val)
            self.checkbox_configs[item[1]] = cfg_item
            # ✨【国际化重构】：这里把前端显示的名称 item[0] 丢进 _() 钩子里翻译
            self.list.append(getConfigListEntry(_(item[0]), cfg_item))
            
        ConfigListScreen.__init__(self, self.list, session=self.session)
        
        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "green": self.start_sync_selected,  
            "ok": self.toggle_current_item,      
            "red": self.close,                    
            "cancel": self.close
        }, -1)

    def toggle_current_item(self):
        current = self["config"].getCurrent()
        if current and current[1]:
            current[1].value = not current[1].value
            self["config"].invalidateCurrent() 

    def load_saved_config(self):
        choices = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and "=" in line:
                            k, v = line.split("=", 1)
                            choices[k] = (v == "True")
            except:
                pass
        return choices

    def save_current_config(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                for item in BOUQUET_LIST:
                    val = self.checkbox_configs[item[1]].value
                    f.write("%s=%s\n" % (item[1], str(val)))
        except:
            pass

    def load_local_sizes(self):
        sizes = {}
        if os.path.exists(SIZE_FILE):
            try:
                with open(SIZE_FILE, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and "=" in line:
                            k, v = line.split("=", 1)
                            sizes[k] = int(v)
            except:
                pass
        return sizes

    def save_local_sizes(self):
        try:
            with open(SIZE_FILE, "w") as f:
                for k, v in self.local_sizes.items():
                    f.write("%s=%d\n" % (k, v))
        except:
            pass

    def get_remote_file_size(self, safe_url):
        try:
            req = urllib.request.Request(safe_url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
            with urllib.request.urlopen(req, timeout=8) as response:
                return int(response.headers.get('Content-Length', 0))
        except:
            return -1

    def start_sync_selected(self):
        self.save_current_config()
        
        selected_items = []
        for item in BOUQUET_LIST:
            if self.checkbox_configs[item[1]].value:
                selected_items.append(item)
                
        if not selected_items:
            # ✨【国际化重构】：弹窗提示国际化
            self.session.open(MessageBox, _("No categories selected, please choose at least one!"), MessageBox.TYPE_ERROR)
            return

        self["status"].setText(_("Smart checking remote file sizes..."))
        
        success_count = 0
        skip_count = 0
        fail_logs = []
        
        for item in selected_items:
            cat = item[1]
            repo = item[2]
            local_tv_file = os.path.join(LOCAL_DIR, "subbouquet.%s.tv" % cat)
            
            # 生成安全的 GitHub URL
            raw_url = "https://raw.githubusercontent.com/%s/%s/%s/%s/subbouquet.%s.tv.gz" % (
                USER, repo, BRANCH, REMOTE_DIR, cat
            )
            parsed = urllib.parse.urlparse(raw_url)
            encoded_path = urllib.parse.quote(parsed.path)
            safe_url = urllib.parse.urlunparse((
                parsed.scheme, parsed.netloc, encoded_path, parsed.params, parsed.query, parsed.fragment
            ))
            
            remote_size = self.get_remote_file_size(safe_url)
            local_size_record = self.local_sizes.get(cat, 0)
            
            if os.path.exists(local_tv_file) and remote_size > 0 and local_size_record == remote_size:
                skip_count += 1
                continue
                
            success, msg = self.download_gz_file(cat, safe_url, remote_size)
            if success:
                success_count += 1
            else:
                # 💡 失败日志里显示翻译后的名字
                fail_logs.append("%s(%s)" % (_(item[0]), msg))
                
        self.save_local_sizes()
        self.build_nested_structure(selected_items)
        self.refresh_e2_db()
        
        # ✨【国际化重构】：状态栏与结果弹窗翻译支持
        status_msg = _("🎉 Smart Sync Done! Downloaded: %d, Skipped: %d") % (success_count, skip_count)
        self["status"].setText(status_msg)
        
        if fail_logs:
            hint = _("Sync finished with partial failures:\n%s") % ", ".join(fail_logs)
            self.session.open(MessageBox, hint, MessageBox.TYPE_WARNING)
        else:
            hint_msg = _("Sync finished successfully!\nDownloaded: %d files\nSkipped: %d unchanged files") % (success_count, skip_count)
            self.session.open(MessageBox, hint_msg, MessageBox.TYPE_INFO, timeout=5)

    def download_gz_file(self, cat, safe_url, remote_size):
        max_retries = 3
        last_error = "Unknown"
        
        for attempt in range(max_retries):
            try:
                local_path = os.path.join(LOCAL_DIR, "subbouquet.%s.tv" % cat)
                
                req = urllib.request.Request(safe_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=12) as response:
                    compressed_data = response.read()
                
                if not compressed_data:
                    last_error = "Empty"
                    continue
                
                content_bytes = gzip.decompress(compressed_data)
                content_text = content_bytes.decode('utf-8', errors='ignore')
                lines = content_text.splitlines()
                
                fixed_lines = ["#NAME %s" % cat]
                for line in lines:
                    if not line.startswith("#NAME"):
                        fixed_lines.append(line)
                        
                with open(local_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(fixed_lines) + "\n")
                
                try:
                    os.chmod(local_path, 0o644)
                except:
                    pass
                
                if remote_size > 0:
                    self.local_sizes[cat] = remote_size
                else:
                    self.local_sizes[cat] = len(compressed_data)
                    
                return True, "OK"
                
            except Exception as e:
                last_error = str(e)
                import time
                time.sleep(1)
                
        return False, last_error

    def build_nested_structure(self, current_active_items):
        root_bouquet_file = os.path.join(LOCAL_DIR, "bouquets.tv")
        root_entry = '#SERVICE 1:7:2:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.github_root_hsck.tv" ORDER BY bouquet\n'
        
        if os.path.exists(root_bouquet_file):
            with open(root_bouquet_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if "userbouquet.github_root_hsck.tv" not in content:
                with open(root_bouquet_file, "a", encoding="utf-8") as f:
                    f.write(root_entry)
        
        sub_root_path = os.path.join(LOCAL_DIR, "userbouquet.github_root_hsck.tv")
        with open(sub_root_path, "w", encoding="utf-8") as f:
            f.write("#NAME %s\n" % ROOT_FOLDER_NAME)
            
            for item in BOUQUET_LIST:
                local_file = os.path.join(LOCAL_DIR, "subbouquet.%s.tv" % item[1])
                if item in current_active_items or os.path.exists(local_file):
                    f.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "subbouquet.%s.tv" ORDER BY bouquet\n' % item[1])

    def refresh_e2_db(self):
        try:
            urllib.request.urlopen("http://127.0.0.1/web/servicelistreload?mode=0", timeout=5)
            urllib.request.urlopen("http://127.0.0.1/web/servicelistreload?mode=4", timeout=5)
        except:
            pass

def main(session, **kwargs):
    session.open(GitHubBouquetNestedScreen)

def Plugins(**kwargs):
    return [
        PluginDescriptor(
            # ✨【国际化重构】：插件管理列表里的名字和简介也支持翻译钩子
            name=_("GitHub Bouquet Nested Downloader"),
            description=_("Supports smart size checking, custom category selection, and persistence."),
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon="plugin.png",
            fnc=main
        )
    ]