#/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Eduardo
22 de Maio de 2017
HyperRayleigh Scattering Analysis
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.widgets import SpanSelector
from matplotlib.lines import Line2D
import numpy as np
import os
from scipy.optimize import curve_fit
import string

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.set_title("HRS Analysis")
        self.set_wmclass("HRS Analysis", "HRS Analysis")

        self.set_border_width(10)
        self.set_default_size(2000, 1000)
        # self.set_position(Gtk.WindowPosition.CENTER)

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

        self.btConcentra = Gtk.Button(label="Select Concentration/Absorption File")
        self.btConcentra.connect("clicked", self.EscolheConc)

        self.btSalva = Gtk.Button(label="Save")
        self.btSalva.connect("clicked", self.Salva)

        self.liststore = Gtk.ListStore(str, str, float, float)
        self.treeview = Gtk.TreeView(model=self.liststore)

        # self.sel = self.treeview.get_selection()
        # self.sel.set_mode(Gtk.SelectionMode.NONE)

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

        self.abs_text = Gtk.CellRendererText()
        self.column_abs = Gtk.TreeViewColumn("A (532)",
                                             self.abs_text, text=3)
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

        self.ax.set_title('HRS Signal')
        self.ax.set_xlabel('$I(\omega)$')
        self.ax.set_ylabel('$I(2\omega)$')

        self.ax.ticklabel_format(style='sci', scilimits=(-2, 2), axis='both')

        self.cv1 = FigureCanvas(self.fg)
        # self.cursor = Cursor(self.ax, useblit=True, horizOn=True,
        #                      color='#ff9896', lw=1.5, alpha=0.9)

        self.fg2 = plt.figure()
        self.ax2 = self.fg2.add_subplot(111)
        self.ax2.set_xlabel('$I(\omega)$')
        self.ax2.set_ylabel('$I(2\omega)$')
        self.line2, = self.ax2.plot([], [], 'o')
        self.ax2.ticklabel_format(style='sci', scilimits=(-2, 2), axis='both')

        self.cv2 = FigureCanvas(self.fg2)

        self.fg4 = plt.figure()
        self.ax4 = self.fg4.add_subplot(111)
        self.ax4.set_xlabel('Concentration')
        self.ax4.set_ylabel('$I(2\omega)/I^2(\omega)$')
        self.line4, = self.ax4.plot([], [], 'ok')
        self.l4 = Line2D([], [], color='red', linewidth=1.5)
        self.ax4.add_line(self.l4)

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

    def Slope(self, x, a):
        return a*x

    def proximo(self, event):
        self.ax2.errorbar(self.ref[:self.IM], self.sgn[:self.IM, 0],
                          yerr=self.sgn[:self.IM, 1], fmt='o')
        self.ax2.plot(self.x, self.y, 'r-', lw=2)
        self.fg2.canvas.draw()

        self.dados = np.column_stack((self.ref, self.sgn[:, 0], self.sgn[:, 1]))
        np.savetxt('%s/Params/%s.quadratic' % (self.foldername, self.filename[:-6]), self.dados, delimiter='\t')

        file = open('%s/Params/%s.fit' % (self.foldername, self.filename[:-6]), 'w')
        file.write('%f\t%f\n' % (self.p[0], np.sqrt(self.pcov[0, 0])))
        file.write('%f\t%f\n' % (self.p[1], np.sqrt(self.pcov[1, 1])))
        file.close()

        self.filepath.set_sensitive(True)
        self.lbEsc.set_sensitive(True)
        self.btBrowse.set_sensitive(True)
        self.btFile.set_sensitive(True)

        self.liststore[self.listline][2] = self.p[0]
        self.quad.append((
            float(self.liststore[self.listline][1]),
            self.liststore[self.listline][2],
            np.sqrt(self.pcov[0, 0])))

        self.listline += 1
        # self.treeview.set_cursor(self.listline)

    def removelast(self, event):
        self.quad.pop()
        self.listline -= 1
        self.liststore[self.listline][2] = 0.0

        self.filepath.set_sensitive(True)
        self.lbEsc.set_sensitive(True)
        self.btBrowse.set_sensitive(True)
        self.btFile.set_sensitive(True)

    def seleciona(self, event):
        self.direc = self.filepath.get_text()

        if self.direc == "":
            self.alertempty()

        else:
            self.set_title(self.direc)

            self.filename = string.split(self.filepath.get_text(), '/')[-1]
            self.foldername = self.direc.replace(self.filename, "")

            self.filepath.set_sensitive(False)
            self.lbEsc.set_sensitive(False)
            self.btBrowse.set_sensitive(False)
            self.btFile.set_sensitive(False)

            try:
                os.mkdir('%s/Params' % self.foldername)
            except:
                pass

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
            self.liststore.clear()
            self.btFile.set_sensitive(True)
            self.quad = []
            self.listline = 0

            self.conc = np.genfromtxt(dialog.get_filename(), dtype=None)
            # self.conc = self.conc[::-1]

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        # self.treeview.set_cursor(self.listline)
        self.concpath = dialog.get_current_folder()

        dialog.destroy()

        dialog2 = Gtk.FileChooserDialog(
            "Select Absorption File", None, Gtk.FileChooserAction.OPEN, (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        dialog2.set_transient_for(self)
        dialog2.set_current_folder(self.concpath)
        response2 = dialog2.run()

        if response2 == Gtk.ResponseType.OK:
            self.Abs = np.genfromtxt(dialog2.get_filename(), dtype=float)
            # self.Abs = self.Abs[::-1]

        elif response2 == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog2.destroy()

        if len(self.conc) == len(self.Abs):
            for i in range(0, len(self.conc)):
                (self.smp, self.phi) = self.conc[i]
                self.A532 = self.Abs[i][1]

                self.liststore.append([str(self.smp),
                                       str(self.phi),
                                       0.0,
                                       self.A532])

        else:
            self.alertconcabs()

    def onselect(self, xmin, xmax):
        self.imin = np.searchsorted(self.ref[:self.IM], xmin)
        self.imax = np.searchsorted(self.ref[:self.IM], xmax)

        self.tempdata = []

        # try:
        self.p, self.pcov = curve_fit(
            self.Parabola,
            self.ref[self.imin:self.imax],
            self.sgn[self.imin:self.imax, 0]) #,
            # sigma=self.sgn[self.imin:self.imax, 1],
            # absolute_sigma=True)

        self.x = np.arange(0, 1.05*max(self.ref), max(self.ref)/11.0)
        self.y = self.Parabola(self.x, *self.p)

        self.line.set_data(self.x, self.y)
        self.fg.canvas.draw()

        self.line4.set_data([], [])
        self.l4.set_data([], [])

        self.fg4.canvas.draw()

        for linha in self.quad:
            self.tempdata.append(linha)

        self.tempdata.append((
            float(self.liststore[self.listline][1]),
            self.p[0],
            np.sqrt(self.pcov[0, 0])))
        self.tempdata = np.array(self.tempdata)

        print(self.tempdata)

        self.lim4 = max(self.tempdata[:, 0])*1.1
        self.x4 = np.arange(0, self.lim4, self.lim4/15)
        self.p4, self.pcov4 = curve_fit(
            self.Slope,
            self.tempdata[:, 0],
            self.tempdata[:, 1])

        self.y4 = self.Slope(self.x4, *self.p4)

        self.l4.set_data(self.x4, self.y4)
        self.line4.set_data(self.tempdata[:, 0], self.tempdata[:, 1])

        self.ax4.relim()  # recompute the ax.dataLim
        self.ax4.autoscale_view()  # update ax4 lim

        self.fg4.canvas.draw()

        # except:
        #     print('intervalo')


    def plota(self):
        print('Analising sample: %s' % self.filepath.get_text())

        self.ax.cla()
        self.ax.set_title('HRS Signal')
        self.ax.set_xlabel('$I(\omega)$')
        self.ax.set_ylabel('$I(2\omega)$')

        self.ax.ticklabel_format(style='sci', scilimits=(-2, 2), axis='both')

        self.span = SpanSelector(self.ax, self.onselect, 'horizontal',
                                 useblit=False, rectprops=dict(
                                     alpha=0.7, facecolor='#aec7e8'))

        self.Imps = np.genfromtxt(self.filepath.get_text(), skip_footer=21)
        self.Impr = np.genfromtxt(self.filepath.get_text()[:-5] + 'r.dat',
                                  skip_footer=22)

        self.ref_temp = np.average(self.Impr, axis=1)
        self.sgn_temp = np.column_stack((
            np.average(self.Imps, axis=1),
            np.std(self.Imps, axis=1, ddof=1)))

        self.medref = np.average(self.ref_temp[2:8])
        self.medsgn = np.average(self.sgn_temp[2:8, 0])

        self.IM = np.where(self.ref_temp == max(self.ref_temp))[0][0]

        # self.sgn = self.sgn_temp[:self.IM, :] - self.medsgn
        # self.ref = self.ref_temp[:self.IM] - self.medref

        self.sgn = self.sgn_temp[self.IM:, :][::-1]
        self.sgn[:, 0] -= self.medsgn
        self.sgn[:, 1] = np.sqrt(self.sgn[:, 1]**2 + 1.0e-12)

        self.ref = self.ref_temp[self.IM:][::-1] - self.medref

        self.sgn[:, 0] = (2*self.sgn[:, 0])/(10**(-self.A532*0.5) + 10**(-self.A532*1.5))
        self.IM = -1

        self.ax.errorbar(self.ref[:self.IM], self.sgn[:self.IM, 0],
                         yerr=self.sgn[:self.IM, 1], fmt='ok-')

        self.line, = self.ax.plot(self.ref[:self.IM],
                                  self.sgn[:self.IM, 0], 'r-', lw=2,
                                  zorder=9)
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

    def alertconcabs(self):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK,
                                   "Unable to import files")
        dialog.format_secondary_text(
            "Please check if concentration and absorption files have the same number of rows")
        dialog.run()

        dialog.destroy()

    def Salva(self, event):

        self.samplename = string.split(self.filename, '_')[0]

        dialog = Gtk.FileChooserDialog(
            "Save file", None, Gtk.FileChooserAction.SAVE, (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        dialog.set_transient_for(self)
        dialog.set_current_name(self.samplename + '.HRS')
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


win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
