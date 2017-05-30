#/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Eduardo
22 de Maio de 2017
HyperRayleigh Scattering Analysis
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
# from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.widgets import SpanSelector, Cursor
import numpy as np
import sys
import os
from scipy.optimize import curve_fit
# import string
# import subprocess

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        # self.hb = Gtk.HeaderBar()
        # self.hb.set_show_close_button(True)
        # self.hb.props.title = "HRS Analysis"
        # self.set_titlebar(self.hb)

        self.set_title("HRS Analysis")
        self.set_wmclass("HRS Analysis", "HRS Analysis")

        self.set_border_width(10)
        self.set_default_size(2000, 1000)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.lbEsc = Gtk.Label(label="Select file:")

        self.filepath = Gtk.Entry()

        self.btBrowse = Gtk.Button(label="Browse")
        self.btBrowse.connect("clicked", self.EscolheAqv)

        self.btFile = Gtk.Button(label="Analyse Files")
        self.btFile.set_sensitive(False)
        self.btFile.connect("clicked", self.seleciona)

        self.buttonOK = Gtk.Button(label="     Next    ")
        self.buttonOK.connect("clicked", self.proximo)

        self.buttonQuit = Gtk.Button(label="Remove Last")
        self.buttonQuit.connect("clicked", self.removelast)

        self.btConcentra = Gtk.Button(label="Select Concentration File")
        self.btConcentra.connect("clicked", self.EscolheConc)

        self.btSalva = Gtk.Button(label="Save")
        self.btSalva.set_sensitive(False)
        self.btSalva.connect("clicked", self.Salva)

        self.quad = []
        self.listline = 0
        self.liststore = Gtk.ListStore(str, str, float)
        self.treeview = Gtk.TreeView(model=self.liststore)

        self.amostra_text = Gtk.CellRendererText()
        self.column_amostra = Gtk.TreeViewColumn("Sample",
                                                 self.amostra_text, text=0)
        self.treeview.append_column(self.column_amostra)

        self.concentra_text = Gtk.CellRendererText()
        self.column_concentra = Gtk.TreeViewColumn("Concentration",
                                                   self.concentra_text, text=1)
        self.treeview.append_column(self.column_concentra)

        self.coef_text = Gtk.CellRendererText()
        self.column_coef = Gtk.TreeViewColumn("Quadratic Coef.",
                                              self.coef_text, text=2)
        self.treeview.append_column(self.column_coef)

        self.bxchose = Gtk.HBox(spacing=6)
        self.boxgraph = Gtk.HBox(spacing=6)
        self.boxsubgraph = Gtk.VBox(spacing=6)
        self.boxV = Gtk.VBox(spacing=6)
        self.bxbutton = Gtk.HBox(spacing=6)
        self.bxTodos = Gtk.HBox(spacing=6)
        self.bxlist = Gtk.VBox(spacing=6)

        self.fg = plt.figure()
        self.ax = self.fg.add_subplot(111)

        self.ax.set_title('HRS Signal')
        self.ax.set_xlabel('$I^2(\omega)$')
        self.ax.set_ylabel('$I(2\omega)$')

        self.ax.ticklabel_format(style='sci', scilimits=(-2, 2), axis='both')

        self.cv1 = FigureCanvas(self.fg)
        self.cursor = Cursor(self.ax, useblit=True, horizOn=True,
                             color='#ff9896', lw=1.5, alpha=0.9)

        self.fg2 = plt.figure()
        self.ax2 = self.fg2.add_subplot(111)
        self.ax2.set_title('HRS Signal Todas')
        self.ax2.set_xlabel('$I^2(\omega)$')
        self.ax2.set_ylabel('$I(2\omega)$')
        self.line2, = self.ax2.plot([], [], 'ok')
        self.ax2.ticklabel_format(style='sci', scilimits=(-2, 2), axis='both')

        self.cv2 = FigureCanvas(self.fg2)

        self.fg4 = plt.figure()
        self.ax4 = self.fg4.add_subplot(111)
        self.ax4.set_title('Coef. Quadratico vs. Concentracao')
        self.line4, = self.ax4.plot([], [], 'ok')
        # self.line4.set_data([], [])
        self.cv4 = FigureCanvas(self.fg4)

        self.bxbutton.pack_end(self.buttonOK, True, True, 0)
        self.bxbutton.pack_end(self.buttonQuit, True, True, 0)

        self.bxchose.pack_start(self.lbEsc, False, True, 0)
        self.bxchose.pack_start(self.filepath, True, True, 0)
        self.bxchose.pack_start(self.btBrowse, False, True, 0)
        self.bxchose.pack_start(self.btFile, False, True, 0)

        self.boxsubgraph.pack_start(self.cv2, True, True, 0)
        self.boxsubgraph.pack_start(self.cv4, True, True, 0)

        self.boxgraph.pack_start(self.cv1, True, True, 0)
        self.boxgraph.pack_start(self.boxsubgraph, True, True, 0)

        self.boxV.pack_start(self.bxchose, False, True, 0)
        self.boxV.pack_start(self.boxgraph, True, True, 0)

        self.bxlist.pack_start(self.btConcentra, False, True, 0)
        self.bxlist.pack_start(self.treeview, True, True, 0)
        self.bxlist.pack_start(self.bxbutton, False, False, 0)
        self.bxlist.pack_end(self.btSalva, False, True, 0)

        self.bxTodos.pack_start(self.boxV, True, True, 0)
        self.bxTodos.pack_start(self.bxlist, False, True, 5)
        self.add(self.bxTodos)

    def Parabola(self, x, a, b):
        return a*x**2 + b

    def Afin(self, x, a, b):
        return a*x + b

    def proximo(self, event):
        self.ax2.errorbar(self.ref[:self.IM]**2, self.sgn[:self.IM, 0],
                          yerr=self.sgn[:self.IM, 1], fmt='ok')
        self.ax2.plot(self.x, self.y, 'r-', lw=2)
        self.fg2.canvas.draw()

        self.filepath.set_sensitive(True)
        self.lbEsc.set_sensitive(True)
        self.btBrowse.set_sensitive(True)
        self.btFile.set_sensitive(True)

        self.liststore[self.listline][2] = self.p[0]
        self.quad.append((float(self.liststore[self.listline][1]),
                          self.liststore[self.listline][2]))

        # self.a = float(self.liststore[self.listline][1])

        # self.ax4.plot(self.a, self.p[0], 'ok')

        # self.fg4.canvas.draw()
        self.listline += 1

    def quit(self, event):
        print('Exit')
        sys.exit()

    def removelast(self, event):
        self.quad.pop()
        self.listline -= 1
        self.liststore[self.listline][2] = 0.0

    def seleciona(self, event):
        if self.filepath.get_text() == "":
            self.alertempty()
        else:
            self.set_title(self.filepath.get_text())
            self.filepath.set_sensitive(False)
            self.lbEsc.set_sensitive(False)
            self.btBrowse.set_sensitive(False)
            self.btFile.set_sensitive(False)
            self.direc = self.filepath.get_text()
            self.ax.cla()
            self.plota()

    def EscolheAqv(self, event):
        dialog = Gtk.FileChooserDialog(
            "Selecione o arquivo", None, Gtk.FileChooserAction.OPEN, (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_transient_for(self)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Signal files")
        filter_any.add_pattern("*s.dat")
        dialog.add_filter(filter_any)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.filepath.set_text(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def EscolheConc(self, event):
        dialog = Gtk.FileChooserDialog(
            "Select Concentration File", None, Gtk.FileChooserAction.OPEN, (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        dialog.set_transient_for(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.btFile.set_sensitive(True)
            self.btSalva.set_sensitive(True)
            self.conc = open(dialog.get_filename(), 'r')
            for line in self.conc:
                (self.smp, self.phi) = line.split()
                # self.phi = float(self.phi)
                self.liststore.append([self.smp, self.phi, 0.0])
                # self.liststore.append([
                #     self.smp, format(self.phi, '.2e'), 0.0])
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def onselect(self, xmin, xmax):
        self.imin = np.searchsorted(self.ref[:self.IM]**2, xmin)
        self.imax = np.searchsorted(self.ref[:self.IM]**2, xmax)

        self.tempdata = []
        print(self.quad)

        try:
            self.p, self.pcov = curve_fit(
                self.Afin,
                self.ref[self.imin:self.imax]**2,
                self.sgn[self.imin:self.imax, 0],
                sigma=self.sgn[self.imin:self.imax, 1],
                absolute_sigma=True)

            self.x = np.arange(0, 2e-4, 1e-6)
            self.y = self.Afin(self.x, *self.p)

            self.line.set_data(self.x, self.y)
            self.fg.canvas.draw()

            self.line4.set_data([], [])
            self.fg4.canvas.draw()

            for linha in self.quad:
                self.tempdata.append(linha)

            self.tempdata.append((float(
                self.liststore[self.listline][1]), self.p[0]))
            self.tempdata = np.array(self.tempdata)

            print(self.tempdata)

            self.line4.set_data(self.tempdata[:, 0], self.tempdata[:, 1])

            # recompute the ax.dataLim
            self.ax4.relim()
            # update ax.viewLim using the new dataLim
            self.ax4.autoscale_view()

            self.fg4.canvas.draw()

        except:
            print('intervalo')

    def plota(self):
        print(self.filepath.get_text())

        self.ax.set_title('HRS Signal')
        self.ax.set_xlabel('$I^2(\omega)$')
        self.ax.set_ylabel('$I(2\omega)$')

        self.ax.ticklabel_format(style='sci', scilimits=(-2, 2), axis='both')

        self.span = SpanSelector(self.ax, self.onselect, 'horizontal',
                                 useblit=True, rectprops=dict(
                                     alpha=0.7, facecolor='#aec7e8'))

        self.Imps = np.genfromtxt(self.filepath.get_text())
        self.Impr = np.genfromtxt(self.filepath.get_text()[:-5] + 'r.dat',
                                  skip_footer=1)

        self.sgn = np.column_stack((np.average(self.Imps, axis=1),
                                    np.std(self.Imps, axis=1)/np.sqrt(
                                        np.shape(self.Imps)[1])))
        self.ref = np.average(self.Impr, axis=1)

        self.ax.plot(self.Impr**2, self.Imps, 'o-', alpha=0.5)

        self.IM = np.where(self.ref == max(self.ref))[0][0]

        self.ax.errorbar(self.ref[:self.IM]**2, self.sgn[:self.IM, 0],
                         yerr=self.sgn[:self.IM, 1], fmt='ok-')

        self.line, = self.ax.plot(self.ref[:self.IM]**2,
                                  self.sgn[:self.IM, 0], 'r-', lw=2,
                                  zorder=9)
        self.line.set_data([], [])

        self.fg.canvas.draw()

    def plotavarios(self):
        self.files = [file for file in sorted(os.listdir(
            self.filepath.get_text())) if file.endswith('s.dat')]

        for aqv in self.files:
            print(aqv)
            dados = np.genfromtxt(self.filepath.get_text() +
                                  '/' + aqv)

            self.line, = self.ax.plot(dados)
            self.ax.draw()
            # print(self.files)

    def alertempty(self):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, "Empy filepath")
        dialog.format_secondary_text(
            "Please select a file to analyse")
        dialog.run()

        dialog.destroy()

    def Salva(self):
        print('salva')

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
