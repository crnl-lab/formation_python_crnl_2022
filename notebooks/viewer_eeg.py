
from ephyviewer import mkQApp, MainViewer, TraceViewer, TimeFreqViewer
from ephyviewer import InMemoryEpochSource, EpochViewer, EventList
import numpy as np
import neo
import scipy.signal

#Import des signaux
filename = './data/File_micromed_1.TRC'
reader = neo.MicromedIO(filename=filename)

seg = reader.read_segment()
anasig = seg.analogsignals[0]
triggers = seg.events[0]


# signaux + signaux filtrés
sr = anasig.sampling_rate.rescale('Hz').magnitude
t_start = anasig.t_start.rescale('s').magnitude
print('sr', sr, 't_start', t_start)
f1, f2 = 5, 49
band = [f1/sr*2., f2/sr*2.]
sigs = anasig.rescale('uV').magnitude

coeff_sos = scipy.signal.iirfilter(8, band, analog=False,
                        btype='bandpass', ftype='butter', output='sos')
filtered_sigs = scipy.signal.sosfiltfilt(coeff_sos, sigs, axis=0)

# main wibndow + QApp
app = mkQApp()
win = MainViewer()

# view1 = signaux
view1 = TraceViewer.from_numpy(sigs, sr, t_start, 'Signals')
view1.params['scale_mode'] = 'same_for_all'
win.add_view(view1)

# view2 = signaux filtrés
view2 = TraceViewer.from_numpy(filtered_sigs, sr, t_start, 'Filtered Signals')
win.add_view(view2)

# view3 = temps fréquences
view3 = TimeFreqViewer.from_numpy(sigs, sr, t_start, 'CWT')
view3.params['display_labels'] = False
win.add_view(view3)

# data source commune à viewer4 et viewer5
epoch = { 'time':triggers.times.rescale('s').magnitude,
                'duration': np.zeros(triggers.times.size),
                'label':triggers.labels,
                'name':'triggers' }
data_source_epoch = InMemoryEpochSource(all_epochs=[epoch])

# view4 = triggers
view4 = EpochViewer(source=data_source_epoch, name='triggers')
win.add_view(view4)

# view5 = list triggers
view5 = EventList(source=data_source_epoch, name='triggers list')
win.add_view(view5, location='bottom',  orientation='horizontal')


#Run
win.show()
app.exec_()