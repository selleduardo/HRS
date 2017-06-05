# /usr/bin/env python
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
import string
# import subprocess

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        # self.hb = Gtk.HeaderBar()
        # self.hb.set_show_close_button(True)
        # self.hb.props.title = "Linear Absorption Analysis"
        # self.set_titlebar(self.hb)

        self.set_title("Linear Absorption Analysis")
        self.set_wmclass("Linear Absorption Analysis",
                         "Linear Absorption Analysis")

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

        self.btSkip = Gtk.Button(label="     Skip    ")
        self.btSkip.connect("clicked", self.skip)

        self.buttonQuit = Gtk.Button(label="Remove Last")
        self.buttonQuit.connect("clicked", self.removelast)

        self.btConcentra = Gtk.Button(label="Select Concentration File")
        self.btConcentra.connect("clicked", self.EscolheConc)

        self.btSalva = Gtk.Button(label="Save")
        self.btSalva.connect("clicked", self.Salva)

        self.liststore = Gtk.ListStore(str, str, float)
        self.treeview = Gtk.TreeView(model=self.liststore)

        self.sel = self.treeview.get_selection()
        self.sel.set_mode(Gtk.SelectionMode.NONE)

        self.amostra_text = Gtk.CellRendererText()
        self.column_amostra = Gtk.TreeViewColumn("Sample",
                                                 self.amostra_text, text=0)
        self.treeview.append_column(self.column_amostra)

        self.concentra_text = Gtk.CellRendererText()
        self.column_concentra = Gtk.TreeViewColumn("Concentration",
                                                   self.concentra_text, text=1)
        self.treeview.append_column(self.column_concentra)

        self.abs_text = Gtk.CellRendererText()
        self.column_abs = Gtk.TreeViewColumn("Abs (532)",
                                             self.abs_text, text=2)
        self.treeview.append_column(self.column_abs)

        self.bxchose = Gtk.HBox(spacing=6)
        self.boxgraph = Gtk.HBox(spacing=6)
        self.boxsubgraph = Gtk.VBox(spacing=6)
        self.boxV = Gtk.VBox(spacing=6)
        self.bxbutton = Gtk.HBox(spacing=6)
        self.bxTodos = Gtk.HBox(spacing=6)
        self.bxlist = Gtk.VBox(spacing=6)

        self.fg = plt.figure()
        self.ax = self.fg.add_subplot(111)

        self.ax.set_title('Absorption Spectrum')
        self.ax.set_xlabel('$\lambda$ (nm)')
        self.ax.set_ylabel('A (O.D)')

        self.cv1 = FigureCanvas(self.fg)
        # self.cursor = Cursor(self.ax, useblit=True, horizOn=True,
        #                      color='#ff9896', lw=1.5, alpha=0.9)

        self.fg2 = plt.figure()
        self.ax2 = self.fg2.add_subplot(111)
        self.ax2.set_title('Absorption Todas')
        self.ax2.set_xlabel('$\lambda$ (nm)')
        self.ax2.set_ylabel('A (O.D)')

        self.line2, = self.ax2.plot([], [])
        # self.ax2.ticklabel_format(style='sci', scilimits=(-2, 2), axis='both')

        self.cv2 = FigureCanvas(self.fg2)

        self.fg4 = plt.figure()
        self.ax4 = self.fg4.add_subplot(111)
        self.ax4.set_title('Beer-Lambert Law')

        self.line4, = self.ax4.plot([], [], 'ok')
        self.cv4 = FigureCanvas(self.fg4)

        self.bxbutton.pack_end(self.buttonOK, True, True, 0)
        self.bxbutton.pack_end(self.btSkip, True, True, 0)
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

    def proximo(self, event):

        self.ax2.plot(self.spect[:, 0], self.corrspect)
        self.fg2.canvas.draw()
        
        self.filepath.set_sensitive(True)
        self.lbEsc.set_sensitive(True)
        self.btBrowse.set_sensitive(True)
        self.btFile.set_sensitive(True)

        self.liststore[self.listline][2] = self.a532
        self.quad.append((
            float(self.liststore[self.listline][1]),
            self.liststore[self.listline][2],
            np.sqrt(self.pcov[0, 0])))

        self.listline += 1

    def quit(self, event):
        print('Exit')
        sys.exit()

    def removelast(self, event):
        self.quad.pop()
        self.listline -= 1
        self.liststore[self.listline][2] = 0.0

        self.filepath.set_sensitive(True)
        self.lbEsc.set_sensitive(True)
        self.btBrowse.set_sensitive(True)
        self.btFile.set_sensitive(True)

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
            self.liststore.clear()
            self.btFile.set_sensitive(True)
            self.quad = []
            self.listline = 0

            self.conc = open(dialog.get_filename(), 'r')

            try:
                for line in self.conc:
                    (self.smp, self.phi) = line.split()
                    # self.phi = float(self.phi)
                    self.liststore.append([self.smp, self.phi, 0.0])
                    # self.liststore.append([
                    #     self.smp, format(self.phi, '.2e'), 0.0])
            except:
                self.alertconc()

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def onselect(self, xmin, xmax):
        self.imin = np.searchsorted(self.spect[:, 0], xmin)
        self.imax = np.searchsorted(self.spect[:, 0], xmax)

        self.i532 = np.searchsorted(self.spect[:, 0], 532)
        self.tempdata = []

        try:
            self.param_bounds=(0, np.inf)
            self.p, self.pcov = curve_fit(
                self.Baseline,
                self.spect[self.imin:self.imax, 0],
                self.spect[self.imin:self.imax, 1])

            self.x = np.arange(300, 1100, 10)
            self.y = self.Baseline(self.x, *self.p)

            self.line.set_data(self.x, self.y)
            self.fg.canvas.draw()

            self.corrspect = self.spect[:, 1] - self.Baseline(self.spect[:, 0],
                                                          *self.p)
            self.a532 = self.corrspect[self.i532]

            self.plotaax2()

            self.line4.set_data([], [])
            self.fg4.canvas.draw()

            for linha in self.quad:
                self.tempdata.append(linha)

            self.tempdata.append((
                float(self.liststore[self.listline][1]),
                self.a532, np.sqrt(self.pcov[0, 0])))

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
        print('Analising sample: %s' % self.filepath.get_text())

        self.ax.set_title('Absorption Spectrum')
        self.ax.set_xlabel('$\lambda$ (nm)')
        self.ax.set_ylabel('A (O.D)')
        self.ax.set_xlim(350, 950)
        self.ax.set_ylim(-0.1, 3)

        self.ax.ticklabel_format(style='sci', scilimits=(-2, 2), axis='both')

        self.span = SpanSelector(self.ax, self.onselect, 'horizontal',
                                 useblit=False, rectprops=dict(
                                     alpha=0.7, facecolor='#aec7e8'))

        self.spect = np.genfromtxt(self.filepath.get_text(), skip_header=2)

        self.ax.plot(self.spect[:, 0], self.spect[:, 1], '-', alpha=0.85)

        self.line, = self.ax.plot(self.spect[:, 0], self.spect[:, 0],
                                  lw=2, zorder=9)

        self.line.set_data([], [])
        # recompute the ax.dataLim
        self.ax.relim()
        # update ax.viewLim using the new dataLim
        self.ax.autoscale_view()

        self.fg.canvas.draw()

    def plotaax2(self):
        self.line2.set_data(self.spect[:, 0], self.corrspect)
        self.ax2.set_xlim(350, 950)
        self.ax2.set_ylim(-0.1, 3)
        # # recompute the ax.dataLim
        # self.ax2.relim()
        # # update ax.viewLim using the new dataLim
        # self.ax2.autoscale_view()
        self.fg2.canvas.draw()

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

    def alertconc(self):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, "Unable to import file")
        dialog.format_secondary_text(
            "Please check if the file has two columns: sample, concentration")
        dialog.run()

        dialog.destroy()

    def Salva(self, event):

        self.filename = string.split(self.filepath.get_text(), '/')[-1]
        self.samplename = string.split(self.filename, '_')[0]

        dialog = Gtk.FileChooserDialog(
            "Save file", None, Gtk.FileChooserAction.SAVE, (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        dialog.set_transient_for(self)
        dialog.set_current_name(self.samplename + '.blb')
        dialog.set_do_overwrite_confirmation(True)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.path = dialog.get_filename()
            print('Saving file: ' + self.path)
            self.salva = np.array(self.quad)
            np.savetxt(self.path, self.salva, delimiter='\t')
            print('Done')
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def skip(self, event):
        self.listline += 1

    def Scat(self, x, a):
        return a/(x**4)

    def Baseline(self, x, a):
        return a

    def Parabola(self, x, a, b):
        return a*x**2 + b

    def Afin(self, x, a, b):
        return a*x + b


win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
