# -*- coding: utf-8 -*-
#
# Portions of this code are derived from the copyrighted works of:
#    Damien Elmes <anki@ichi2.net>
#
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
#
# Bulk generate cloze
# Written by Ryan Smith
# rnsmith2@gmail.com
# http://github.com/tanzoniteblack/
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from anki.hooks import addHook
from aqt import mw
import re
import random

clozeFields = ["Text"]

clozeRegex = re.compile("{{c\d+::[^}]+}}", flags=re.UNICODE)
wordSplitregex = re.compile("\W+", flags=re.UNICODE)


def containsCloze(fieldText):
    """Returns boolean value about whether field's text already contains a cloze."""
    if clozeRegex.search(fieldText):
        return True
    return False


def generateCloze(fieldText):
    """Pick a word (more or less at random) and generate a cloze for it. Skip words which begin a sentence."""
    words = {word for word in wordSplitregex.split(fieldText.strip())[1:] if len(word) > 2}
    if len(words) < 1:
        return fieldText
    wordToReplace = random.sample(words, 1)[0]
    if not wordToReplace:
        return fieldText
    withCloze = re.sub(ur'\b(?i)(?P<clz>{})\b'.format(wordToReplace), u"{{c1::\g<clz>}}", fieldText, flags=re.UNICODE)
    return withCloze

    # Bulk updates
##########################################################################


def bulkGenerateClozes(nids):
    mw.checkpoint("Bulk-add clozes")
    mw.progress.start()
    for nid in nids:
        note = mw.col.getNote(nid)
        src = None
        for fld in clozeFields:
            if fld in note:
                src = fld
                break
        if not src:
            # no src field
            continue
        srcTxt = mw.col.media.strip(note[src])
        if not srcTxt.strip():
            continue
        if containsCloze(srcTxt):
            # already contains cloze, skip
            continue
        try:
            note[src] = generateCloze(srcTxt)
        except Exception, e:
            raise
        note.flush()
    mw.progress.finish()
    mw.reset()


def setupMenu(browser):
    a = QAction("Bulk-add clozes", browser)
    browser.connect(a, SIGNAL("triggered()"), lambda e=browser: onRegenerate(e))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


def onRegenerate(browser):
    bulkGenerateClozes(browser.selectedNotes())

addHook("browser.setupMenus", setupMenu)
