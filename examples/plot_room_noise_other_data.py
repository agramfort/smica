import numpy as np
from os import path as op
import matplotlib.pyplot as plt
from smica import ICA, transfer_to_ica, SOBI_mne, JDIAG_mne, dipolarity
import mne

from mne.preprocessing import ICA as ICA_mne

from mne.datasets import multimodal, sample

from picard import picard

from sklearn.decomposition import fastica


# raw_fname = os.path.join(multimodal.data_path(), 'multimodal_raw.fif')
n_bins = 40
n_components = 40
freqs = np.linspace(1, 60, n_bins + 1)

data_path = sample.data_path()
fname_bem = op.join(data_path, 'subjects', 'sample', 'bem',
                    'sample-5120-bem-sol.fif')
raw_fname = data_path + '/MEG/sample/sample_audvis_raw.fif'
rc = {"pdf.fonttype": 42, 'text.usetex': False, 'font.size': 14,
      'xtick.labelsize': 12, 'ytick.labelsize': 12, 'text.latex.preview': True}

plt.rcParams.update(rc)

colors = ['indianred', 'cornflowerblue', 'k']


def plot_powers(powers, noise_sources, muscle_source, ax, title):
    cols = []
    for i in range(n_components):
        if i in noise_sources:
            cols.append(colors[2])
        elif i in muscle_source:
            cols.append(colors[1])
        else:
            cols.append(colors[0])
    for p, col in zip(powers.T, cols):
        ax.semilogy(freqs[1:], p, color=col)
    ax.semilogy([], [], color=colors[0], label='Brain sources')
    ax.semilogy([], [], color=colors[1], label='Muscle source')
    ax.semilogy([], [], color=colors[2], label='Room noise')
    x_ = ax.set_xlabel('Frequency (Hz.)')
    y_ = ax.set_ylabel('Power')
    t_ = ax.set_title(title)
    ax.set_xlim([0, freqs.max()])
    ax.grid()
    plt.savefig('figures/%s.pdf' % title, bbox_extr_artists=[x_, y_, t_],
                bbox_inches='tight')
    # ax.legend(loc='upper center', ncol=2)


# fetch data
raw = mne.io.read_raw_fif(raw_fname, preload=True)
picks = mne.pick_types(raw.info, meg='mag', eeg=False, eog=False,
                       stim=False, exclude='bads')

# Compute ICA on raw: chose the frequency decomposition. Here, uniform between
# 2 - 35 Hz.
#
jdiag = JDIAG_mne(n_components=n_components, freqs=freqs, rng=0)
jdiag.fit(raw, picks=picks, verbose=True, tol=1e-9, max_iter=1000)


smica = ICA(n_components=n_components, freqs=freqs, rng=0)
smica.fit(raw, picks=picks, verbose=100, tol=1e-10, em_it=100000)

# Plot powers

# noise_sources = [6, 8, 9]
# muscle_source = [7]
# f, ax = plt.subplots(figsize=(4, 2))
# plot_powers(smica.powers, noise_sources, muscle_source, ax, 'smica')
# plt.show()
# #
# #
# sobi = SOBI_mne(100, n_components, freqs, rng=0)
# sobi.fit(raw, picks=picks)
raw.filter(2, 70)
ica = ICA_mne(n_components=n_components, method='fastica', random_state=0)
ica.fit(raw, picks=picks)

ica_mne = transfer_to_ica(raw, picks, freqs,
                          ica.get_sources(raw).get_data(),
                          ica.get_components())


brain_sources = smica.compute_sources()
K, W, _ = picard(brain_sources, ortho=False, verbose=True, random_state=0,
                 max_iter=1000)
picard_mix = np.linalg.pinv(W @ K)
A_wiener = smica.A.dot(picard_mix)
gof_wiener = dipolarity(A_wiener, raw, picks, fname_bem, n_jobs=3)[0]

brain_sources = smica.compute_sources(method='pinv')
K, W, _ = picard(brain_sources, ortho=False, verbose=True, random_state=0,
                 max_iter=1000)
picard_mix = np.linalg.pinv(W @ K)
A_pinv = smica.A.dot(picard_mix)
gof_pinv = dipolarity(A_pinv, raw, picks, fname_bem, n_jobs=3)[0]

brain_sources = jdiag.compute_sources(raw.get_data(picks=picks), method='pinv')
K, W, _ = picard(brain_sources, ortho=False, verbose=True, random_state=0,
                 max_iter=1000)
picard_mix = np.linalg.pinv(W @ K)
A_pca = jdiag.A.dot(picard_mix)
gof_pca = dipolarity(A_pca, raw, picks, fname_bem, n_jobs=3)[0]

gof_smica = dipolarity(smica.A, raw, picks, fname_bem, n_jobs=3)[0]
gof_jdiag = dipolarity(jdiag.A, raw, picks, fname_bem, n_jobs=3)[0]
# gof_sobi = dipolarity(sobi.A, raw, picks, fname_bem, n_jobs=3)[0]
