# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import os
import gettext

# 1. 定义你的插件专属域
PluginLanguageDomain = "GitHubBouquet"

# 2. 动态寻找盒子里当前插件的语言包路径
PluginLanguagePath = resolveFilename(SCOPE_PLUGINS, "Extensions/GitHubBouquet/locale")

def localeInit():
    lang = language.getLanguage()[:2]
    os.environ["LANGUAGE"] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)
    gettext.textdomain(PluginLanguageDomain)
    # ✨ 使用 try-except 保护，或者直接删掉这一行。在 Python 3 下它已经不需要了
    try:
        gettext.bind_textdomain_codeset(PluginLanguageDomain, "UTF-8")
    except AttributeError:
        pass

def _(txt):
    # 核心翻译钩子：如果在语言包里找到了对应的翻译就返回中文，找不到就直接原样返回英文
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t

# 初始化语言包
localeInit()