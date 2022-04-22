try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

from mne import read_epochs_eeglab
from mne.io import read_raw
from mne.io.eeglab.eeglab import _check_load_mat
from mne.preprocessing import read_ica_eeglab
import numpy as np
from scipy.io import loadmat

from mne_icalabel.features import retrieve_eeglab_icawinv, compute_ica_activations


# Raw/Epochs files with ICA decomposition
raw_eeglab_path = str(files("mne_icalabel.tests").joinpath("data/datasets/sample-raw.set"))
epo_eeglab_path = str(files("mne_icalabel.tests").joinpath("data/datasets/sample-epo.set"))

# ICA activation matrix for raw/epochs
raw_icaact_eeglab_path = str(
    files("mne_icalabel.tests").joinpath("data/icaact/icaact-raw.mat")
)
epo_icaact_eeglab_path = str(
    files("mne_icalabel.tests").joinpath("data/icaact/icaact-epo.mat")
)


def test_retrieve_eeglab_icawinv():
    """Test that the icawinv is correctly retrieved from an MNE ICA object."""
    # Raw instance
    ica = read_ica_eeglab(raw_eeglab_path)
    icawinv, _ = retrieve_eeglab_icawinv(ica)

    eeg = _check_load_mat(raw_eeglab_path, None)
    assert np.allclose(icawinv, eeg.icawinv)

    # Epoch instance
    ica = read_ica_eeglab(epo_eeglab_path)
    icawinv, _ = retrieve_eeglab_icawinv(ica)
    eeg = _check_load_mat(epo_eeglab_path, None)
    assert np.allclose(icawinv, eeg.icawinv)


def test_compute_ica_activations():
    """Test that the icaact is correctly retrieved from an MNE ICA object."""
    # Raw instance
    raw = read_raw(raw_eeglab_path)
    ica = read_ica_eeglab(raw_eeglab_path)
    icaact = compute_ica_activations(raw, ica)

    icaact_eeglab = loadmat(raw_icaact_eeglab_path)["icaact"]
    assert np.allclose(icaact, icaact_eeglab, rtol=1e-8, atol=1e-4)

    # Epoch instance
    epochs = read_epochs_eeglab(epo_eeglab_path)
    ica = read_ica_eeglab(epo_eeglab_path)
    icaact = compute_ica_activations(epochs, ica)

    icaact_eeglab = loadmat(epo_icaact_eeglab_path)["icaact"]
    assert np.allclose(icaact, icaact_eeglab, rtol=1e-8, atol=1e-4)
