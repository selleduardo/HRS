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
import string
# import subprocess

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.set_title("Baseline")
        self.set_wmclass("Baseline", "Baseline")

        self.set_border_width(10)
        self.set_default_size(2000, 1000)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.lbEsc = Gtk.Label(label="Select file:")

        self.filepath = Gtk.Entry()

        self.btBrowse = Gtk.Button(label="Browse")
        self.btBrowse.connect("clicked", self.EscolheAqv)

        self.btFile = Gtk.Button(label="Analyse Files")
        self.btFile.connect("clicked", self.seleciona)

        self.buttonOK = Gtk.Button(label="OK")
        self.buttonOK.connect("clicked", self.proximo)

        self.btSalva = Gtk.Button(label="Save")
        self.btSalva.connect("clicked", self.Salva)

        self.bxchose = Gtk.HBox(spacing=6)
        self.boxplot = Gtk.VBox(spacing=6)        
        self.boxV = Gtk.VBox(spacing=6)
        self.bxbutton = Gtk.HBox(spacing=6)

        self.fg = plt.figure()
        self.ax = self.fg.add_subplot(111)

        self.ax.set_title('Signal')

        self.ax.ticklabel_format(style='sci', scilimits=(-2, 2), axis='both')

        self.cv1 = FigureCanvas(self.fg)
        # self.cursor = Cursor(self.ax, useblit=True, horizOn=True,
        #                      color='#ff9896', lw=1.5, alpha=0.9)


        self.bxchose.pack_start(self.lbEsc, False, True, 0)
        self.bxchose.pack_start(self.filepath, True, True, 0)
        self.bxchose.pack_start(self.btBrowse, False, True, 0)
        self.bxchose.pack_start(self.btFile, False, True, 0)

        self.bxbutton.pack_start(self.buttonOK, True, True, 0)
        self.bxbutton.pack_start(self.btSalva, True, True, 0)

        self.boxplot.pack_start(self.cv1, True, True, 0)

        self.boxV.pack_start(self.bxchose, False, True, 0)
        self.boxV.pack_start(self.boxplot, True, True, 0)
        self.boxV.pack_start(self.bxbutton, False, True, 0)

        self.add(self.boxV)


    def proximo(self, event):

        self.sgn[:, 1] = self.sgn[:, 1] - self.Baseline(self.sgn[:, 0], *self.p)

        self.ax.cla()
        self.ax.plot(self.sgn[:, 0], self.sgn[:, 1])
        self.fg.canvas.draw()

        self.boxplot.set_sensitive(False)

        self.filepath.set_sensitive(True)
        self.lbEsc.set_sensitive(True)
        self.btBrowse.set_sensitive(True)
        self.btFile.set_sensitive(True)

    def seleciona(self, event):
        if self.filepath.get_text() == "":
            self.alertempty()
        else:
            self.boxplot.set_sensitive(True)
            self.set_title(self.filepath.get_text())
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

    def onselect(self, xmin, xmax):
        self.imin = np.searchsorted(self.sgn[:, 0], xmin)
        self.imax = np.searchsorted(self.sgn[:, 0], xmax)

        try:
            self.p, self.pcov = curve_fit(
                self.Baseline,
                self.sgn[self.imin:self.imax, 0],
                self.sgn[self.imin:self.imax, 1])

            self.lims = self.ax.get_xlim()
            self.x = np.arange(self.lims[0], self.lims[1], self.lims[1]/11.0)
            self.y = self.Baseline(self.x, *self.p)

            self.line.set_data(self.x, self.y)
            self.fg.canvas.draw()

        except:
            print('Not able to fit. Try again')


    def plota(self):
        print('Analising sample: %s' % self.filepath.get_text())
        self.ax.cla()

        self.span = SpanSelector(self.ax, self.onselect, 'horizontal',
                                 useblit=False, rectprops=dict(
                                     alpha=0.7, facecolor='#aec7e8'))

        self.Imps = np.genfromtxt(self.filepath.get_text())

        self.sgn = np.column_stack((
            np.arange(0, np.shape(self.Imps)[0]),
            np.average(self.Imps, axis=1)))

        self.ax.plot(self.sgn[:, 0], self.sgn[:, 1], '-')
        self.ax.relim()
        self.ax.autoscale_view()

        self.line, = self.ax.plot(self.sgn[:, 0], self.sgn[:, 1], '-')
        self.line.set_data([], [])
        self.fg.canvas.draw()

    def alertempty(self):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, "Empy filepath")
        dialog.format_secondary_text(
            "Please select a file to analyse")
        dialog.run()

        dialog.destroy()

    def alertconc(self):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK,
                                   "Unable to import file")
        dialog.format_secondary_text(
            "Please check if the concentration file has columns: (sample, concentration) and absorbption file (sample, A532nm)")
        dialog.run()

        dialog.destroy()

    def Salva(self, event):

        self.filename = string.split(self.filepath.get_text(), '/')[-1]

        dialog = Gtk.FileChooserDialog(
            "Save file", None, Gtk.FileChooserAction.SAVE, (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        dialog.set_transient_for(self)
        dialog.set_current_name(self.filename)
        dialog.set_do_overwrite_confirmation(True)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.path = dialog.get_filename()
            print('Saving file: ' + self.path)
            np.savetxt(self.path, self.sgn, delimiter='\t')
            print('Done')
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()


    def Parabola(self, x, a, b):
        return a*x**2 + b

    def Baseline(self, x, a):
        return a*x/x



win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
