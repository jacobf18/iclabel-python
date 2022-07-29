import os.path as op

import matplotlib.pyplot as plt
import pytest
from mne.datasets import testing
from mne.io import read_raw_edf
from mne.preprocessing import ICA
from mne.utils import requires_version

import mne_icalabel


@pytest.fixture
def _label_ica_components():
    # Use a fixture to create these classes so we can ensure that they
    # are closed at the end of the test
    guis = list()

    def fun(*args, **kwargs):
        guis.append(mne_icalabel.gui.label_ica_components(*args, **kwargs))
        return guis[-1]

    yield fun

    for gui in guis:
        try:
            gui.close()
        except Exception:
            pass


@pytest.fixture(scope="module")
def load_raw_and_fit_ica():
    data_path = op.join(testing.data_path(), "EDF")
    raw_fname = op.join(data_path, "test_reduced.edf")
    raw = read_raw_edf(raw_fname, preload=True)

    # high-pass filter
    raw.filter(l_freq=1, h_freq=100)

    # compute ICA
    ica = ICA(n_components=15, random_state=12345)
    ica.fit(raw)
    return raw, ica


@pytest.fixture(scope="function")
def _fitted_ica(load_raw_and_fit_ica):
    raw, ica = load_raw_and_fit_ica
    return raw, ica.copy()


@requires_version("mne", "1.1dev0")
@testing.requires_testing_data
def test_label_components_gui_io(_fitted_ica, _label_ica_components):
    """Test the input/output of the labeling ICA components GUI."""
    # get the Raw and fitted ICA instance
    raw, ica = _fitted_ica
    ica_copy = ica.copy()

    with pytest.raises(ValueError, match="ICA instance should be fit on"):
        ica_copy.current_fit = "unfitted"
        _label_ica_components(raw, ica_copy)


@requires_version("mne", "1.1dev0")
@testing.requires_testing_data
def test_label_components_gui_display(_fitted_ica, _label_ica_components):
    raw, ica = _fitted_ica

    # test functions
    gui = _label_ica_components(raw, ica)

    # test setting the label
    assert gui.inst == raw
    assert gui.ica == ica
    assert gui.n_components_ == ica.n_components_

    # the initial component should be 0
    assert gui.selected_component == 0

    # there should be three figures inside the QT window
    figs = list(map(plt.figure, plt.get_fignums()))
    assert len(figs) == 3
