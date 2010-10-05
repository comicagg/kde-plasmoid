# -*- coding: utf-8 -*-
# Copyright (C) 2010  Jesús Fernández <jesusfs@gmail.com>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

#Uses code from gmail-plasmoid by Mark McCans http://code.google.com/p/gmail-plasmoid

#import kde and qt specific stuff
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from PyQt4.QtNetwork import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

#import commands for executing shell commands
from dbus.mainloop.qt import DBusQtMainLoop
DBusQtMainLoop(set_as_default=True)

from comicaggconfig import ComicaggConfig
import urllib, os, commands, shutil
from dialog import PopupDialog

#Plasmoid gained by inheritance
class ComicaggPlasmoid(plasmascript.Applet):

	def __init__(self, parent, args=None):
		plasmascript.Applet.__init__(self, parent)

	def init(self):
		self.installIconFile()
		#enable settings dialog
		self.setHasConfigurationInterface(True)
		#set size of Plasmoid
		self.resize(32, 32)
		#set aspect ratio mode
		self.setAspectRatioMode(Plasma.Square)

		self.theme = Plasma.Svg(self)
		self.theme.setImagePath("widgets/background")
		self.setBackgroundHints(Plasma.Applet.TranslucentBackground)
		self.layout = QGraphicsLinearLayout(Qt.Vertical, self.applet)
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(1, 1, 1, 1)
		self.applet.setLayout(self.layout)

		# Create the dialog to display information on hover
		self.dialog = PopupDialog()
		self.dialog.init()
		self.dialogTimer = QTimer()
		self.connect(self.dialogTimer, SIGNAL("timeout()"), self.showDialog)

		self.cfg = self.config("comicagg-notifier")
		self.create_icon()

		# Setup translations
		vers = {}
		vers["en"] = "1"
		vers["es"] = "2"
		kdehome = unicode(KGlobal.dirs().localkdedir())
		self.installTranslation(vers, unicode(KGlobal.locale().language()), kdehome)
		KGlobal.locale().insertCatalog("comicagg-plasmoid")

		self.check_config()
		#update every 15 mins
		self.interval = 15 * 60 * 1000
		self.comics_number = -1
		if self.user:
			self.timer = self.startTimer(self.interval)
			self.update_comics()
		else:
			self.timer = 0
		self.change_icon()

	# # # # # #
	# Tooltip #
	# # # # # #

	def hoverEnterEvent(self, event):
		"""Show the tooltip dialog after one second
		"""
		self.dialogTimer.start(1000)

	def showDialog(self):
		"""Show the tooltip
		"""
		self.dialog.move(self.popupPosition(self.dialog.sizeHint()))
		self.dialog.showDialog()

	def hoverLeaveEvent(self, event):
		"""Hide the tooltip
		"""
		self.dialogTimer.stop()
		self.dialog.hide()

	# # # # # # # # #
	# Configuration #
	# # # # # # # # #

	def check_config(self):
		self.user = self.cfg.readEntry("username") or None
		self.updateTitle()
		print "comicagg-notifier: user:", self.user


	def createConfigurationInterface(self, parent):
		"""Create configuration dialog
		"""
		self.config = ComicaggConfig(self)
		self.config.user.setText(str(self.cfg.readEntry("username")))
		parent.addPage(self.config, i18n("Configuration"), "configure")
		#connect signals
		self.connect(parent, SIGNAL("okClicked()"), self.configAccepted)
		self.connect(parent, SIGNAL("cancelClicked()"), self.configDenied)

	def configAccepted(self):
		"""Do something with the changed config
		"""
		self.user = self.config.user.text() or None
		self.updateTitle()
		self.cfg.writeEntry("username", self.user)
		self.cfg.sync()
		if self.user:
			#update comics
			self.update_comics()
			#remove timer
			self.killTimer(self.timer)
			#start timer agai 
			self.startTimer(self.interval)
		else:
			self.change_icon()

	def configDenied(self):
		"""We do nothing right now.
		"""
		pass

	# # # # # # # # #
	# Updates stuff #
	# # # # # # # # #

	def create_icon(self):
		self.icon = Plasma.IconWidget()
		self.icon.installEventFilter(self)
		#idle icon, there's nothing new
		iconpath = self.package().path() + "contents/res/color.png"
		self.icon_color = iconpath
		#for when we have new comics
		iconpath = self.package().path() + "contents/res/color-washed.png"
		self.icon_washed = iconpath
		#icon for errors
		iconpath = self.package().path() + "contents/res/gris.png"
		self.icon_gray = QIcon(iconpath)
		#add the button to the layout
		self.layout.addItem(self.icon)
		#connect clicked() signal
		QObject.connect(self.icon, SIGNAL("clicked()"), self.onclick)

	def onclick(self):
		"""Do something when clicked
		"""
		#QDesktopServices.openUrl(QUrl("http://dev.comicagg.com"))
		if self.user:
			#update comics
			self.update_comics()
			#remove timer
			self.killTimer(self.timer)
			#start timer agai 
			self.startTimer(self.interval)

	def eventFilter(self, obj, event):
		"""With this event filter we can check if the icon was clicked with the
		middle mouser and if it was, launch the browser.
		"""
		if obj == self.icon:
			if event.type() == QEvent.GraphicsSceneMousePress:
				if event.buttons() == Qt.MidButton:
					QDesktopServices.openUrl(QUrl("http://dev.comicagg.com"))
					return True
		return False

	def timerEvent(self, timer):
		"""When the timer goes off, try an update
		"""
		self.update_comics()

	def updateTitle(self):
		"""Change the title in the tooltip, say, the bold text
		"""
		if not self.user:
			self.user = ""
			self.dialog.setTitle(i18n("No user"))
			self.dialog.setBody(i18n("You need to setup your username"))
		else:
			self.dialog.setTitle(i18n("Comics for ") + self.user)

	def update_comics(self):
		"""Check for an update
		"""
		print "comicagg-notifier: updating..."
		self.comics_number = 0
		url = "http://comicagg.com/ws/" + urllib.quote(str(self.user)) + "/unread"
		manager = QNetworkAccessManager(self)
		QObject.connect(manager, SIGNAL("finished(QNetworkReply *)"), self.reply_finished)
		manager.get(QNetworkRequest(QUrl(url)))

	def reply_finished(self, reply):
		"""Callback to process the reply...
		"""
		if reply.error() == QNetworkReply.NoError:
			self.doc = QDomDocument("unreads")
			cont = reply.readAll()
			self.doc.setContent(cont)
			self.comics_number = int(self.doc.documentElement().attribute("count"))
			self.change_icon()
		elif reply.error() == QNetworkReply.ContentNotFoundError:
			print "comicagg-notifier: got error"
			self.user = None
			self.change_icon()
			self.dialog.setBody(i18n("Error. Is username ok?"))
		else:
			print "comicagg-notifier: got error"
			self.user = None
			self.change_icon()
			self.dialog.setBody(i18n("Error. Is network ok?"))

	def change_icon(self):
		"""Change the icon depending on the state where in
		"""
		if self.user:
			#user configured
			if self.comics_number > 0:
				pix = QPixmap(self.icon_washed)
				painter = QPainter(pix)
				painter.setRenderHint(QPainter.SmoothPixmapTransform)
				painter.setRenderHint(QPainter.Antialiasing)

				font = QFont("sans-serif")
				size = (pix.width() * 60) / 100
				font.setPixelSize(size)
				font.setBold(True)

				# Check if the font is too big
				fm = QFontMetrics(font)
				if fm.width(str(self.comics_number)) > pix.width():
					while fm.width(str(self.comics_number)) > pix.width() and size > 0:
						size = size - 1
						font.setPointSize(size)
						fm = QFontMetrics(font)

				painter.setFont(font)

				painter.setPen(QColor(217, 22, 0))
				painter.setPen(QColor(255, 255, 255))
				x = pix.rect().x()
				y = pix.rect().y()
				w = pix.width()
				h = pix.height()
				painter.drawText(x-2, y, w, h, Qt.AlignVCenter | Qt.AlignHCenter, str(self.comics_number))
				painter.drawText(x+2, y, w, h, Qt.AlignVCenter | Qt.AlignHCenter, str(self.comics_number))
				painter.drawText(x, y+2, w, h, Qt.AlignVCenter | Qt.AlignHCenter, str(self.comics_number))
				painter.drawText(x, y-2, w, h, Qt.AlignVCenter | Qt.AlignHCenter, str(self.comics_number))

				painter.setPen(QColor(255, 96, 0))
				painter.setPen(QColor(0, 0, 0))
				painter.drawText(pix.rect(), Qt.AlignVCenter | Qt.AlignHCenter, str(self.comics_number))

				painter.end()
				body = i18n("<b>%1 unread comics:</b><ul>").arg(self.comics_number)
				comics = self.doc.documentElement().childNodes()
				limit = comics.length()
				if comics.length() > 5:
					limit = 5
				for i in range(0, limit):
					body += "<li>" + comics.item(i).attributes().namedItem("name").nodeValue() + "</li>"
				a = comics.length() - 5
				if a > 0:
					body += i18n("<ul><b>...and %1 more comics</b>").arg(a)
				self.icon.setIcon(QIcon(pix))
				self.dialog.setBody(body)
			else:
				self.icon.setIcon(QIcon(self.icon_color))
				self.dialog.setBody(i18n("No new comics"))
		else:
			self.icon.setIcon(self.icon_gray)
			self.dialog.setBody(i18n("You need to setup your username"))

	# # # # # # # # # # # # #
	# Internationalization  #
	# # # # # # # # # # # # #

	def installTranslation(self, trans, lang, kdehome):
		"""Copied from gmail-plasmoid
		"""
		if lang == "en":
			#print "installTranslation en nothing to do"
			pass
		elif trans.has_key(lang):
			# Setup error message for each translation
			# This is hard coded so that a translated message is displayed even if the translation has not installed.
			transerror = {}
			transerror["default"] = "There was a problem installing a translation for the comicagg-plasmoid widget. Installing the translation requires the 'msgfmt' command, which is included in the 'gettext' package.\n\nPlease ensure that the 'gettext' package is installed."
			transerror["es"] = "Hubo un problema instalando la traducción al español para el widget comicagg-plasmoid, pues se requiere el programa \"msgfmt\", incluido en el paquete \"gettext\".\n\nPor favor, asegúrese de que dicho paquete está instalado."

			# Check if file already exists
			gc = self.config()
			if not os.path.exists(kdehome+"share/locale/"+lang+"/LC_MESSAGES/comicagg-plasmoid.mo"):
				print "Installing "+lang+" translations..."

				# Create required directories
				self.createDirectory(kdehome+"share/locale")
				self.createDirectory(kdehome+"share/locale/"+lang)
				self.createDirectory(kdehome+"share/locale/"+lang+"/LC_MESSAGES")

				# Create .mo file (requires gettext package)
				cmd = unicode("msgfmt -o "+kdehome+"share/locale/"+lang+"/LC_MESSAGES/comicagg-plasmoid.mo"+" "+self.package().path()+"contents/code/i18n/"+lang+"/comicagg-plasmoid.po")
				#print "Command:", cmd
				out = commands.getstatusoutput(cmd)
				if out[0] == 0:
					print "Translation installed."
					gc.writeEntry("trans-"+lang, trans[lang])
				else:
					print "Error installing translation:", out
					if transerror.has_key(lang):
						KMessageBox.informationWId(0, transerror[lang], i18n("Error"), "comicagg-plasmoid-translation-error")
					else:
						KMessageBox.informationWId(0, transerror["default"], i18n("Error"), "comicagg-plasmoid-translation-error")
			else:
				#print "translation exists"
				# Update the file version does not match
				ver = gc.readEntry("trans-"+lang, "0")
				if ver <> trans[lang]:
					#print "Updating "+lang+" translation..."

					# Create .mo file (requires gettext package)
					cmd = unicode("msgfmt -o "+kdehome+"share/locale/"+lang+"/LC_MESSAGES/comicagg-plasmoid.mo"+" "+self.package().path()+"contents/code/i18n/"+lang+"/comicagg-plasmoid.po")
					#print "Command:", cmd
					out = commands.getstatusoutput(cmd)
					if out[0] == 0:
						#print "Translation updated."
						gc.writeEntry("trans-"+lang, trans[lang])
					else:
						#print "Error updating translation:", out
						if transerror.has_key(lang):
							KMessageBox.informationWId(0, transerror[lang], i18n("Error"), "comicagg-plasmoid-translation-error")
						else:
							KMessageBox.informationWId(0, transerror["default"], i18n("Error"), "comicagg-plasmoid-translation-error")
		else:
			#print "No "+lang+" translations exist."
			pass

	def createDirectory(self, d):
		if not os.path.isdir(d):
			try:
				os.mkdir(d)
			except:
				print "Problem creating directory: "+d
				print "Unexpected error:", sys.exc_info()[0]

	# # # # # # # # #
	# Other stuff   #
	# # # # # # # # #

	def installIconFile(self):
		"""
		"""
		#check the file exists
		#kdehome = unicode(KGlobal.dirs().localkdedir())
		#idir = os.path.join(kdehome, "share/icons/hicolor/48x48/apps")
		idir =  str(KGlobal.dirs().resourceDirs("xdgdata-icon")[0])
		ipath = os.path.join(idir, "comicagg-notifier.png")
		if not os.path.exists(ipath):
			#if it doesnt copy the icon from res
			try:
				os.makedirs(idir)
			except:
				pass
			ires = os.path.join(str(self.package().path()), "contents/res/color-48.png")
			shutil.copy(ires, ipath)

def CreateApplet(parent):
	return ComicaggPlasmoid(parent)
