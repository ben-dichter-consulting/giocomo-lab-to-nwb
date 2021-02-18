from pynwb import NWBHDF5IO


def test_nwb_ophys(nwbfile_path):

    with NWBHDF5IO(str(nwbfile_path),'r') as io:
        nwbfile = io.read()
        assert isinstance(nwbfile.subject.fields,dict)
        assert 'subject_id' in nwbfile.subject.fields
        #test 2 photon series:
        assert len(nwbfile.acquisition['TwoPhotonSeries'].data.shape)==3
        #test ophys:
        assert set(nwbfile.processing['ophys'].data_interfaces.keys()) == {'Fluorescence', 'ImageSegmentation','SegmentationImages'}
        assert set(nwbfile.processing['ophys']['Fluorescence'].roi_response_series.keys()) == {'Deconvolved', 'Neuropil', 'RoiResponseSeries'}
        assert nwbfile.processing['ophys']['Fluorescence'].roi_response_series['Deconvolved'].data.shape== \
               nwbfile.processing['ophys']['Fluorescence'].roi_response_series['Neuropil'].data.shape
        assert nwbfile.processing['ophys']['Fluorescence'].roi_response_series['RoiResponseSeries'].data.shape == \
               nwbfile.processing['ophys']['Fluorescence'].roi_response_series['Neuropil'].data.shape
        assert nwbfile.processing['ophys']['ImageSegmentation']['PlaneSegmentation']['image_mask'].data.shape[0]== \
               nwbfile.processing['ophys']['Fluorescence'].roi_response_series['RoiResponseSeries'].data.shape[-1]
        assert set(nwbfile.processing['ophys']['ImageSegmentation']['PlaneSegmentation']['image_mask'].data.shape[1:])==\
                set(nwbfile.processing['ophys']['SegmentationImages']['correlation'].data.shape)
        #test behavior:
        assert len(nwbfile.processing['behavior']['BehavioralTimeSeries'].time_series.keys())>0
        sample_beh_key = list(nwbfile.processing['behavior']['BehavioralTimeSeries'].time_series.keys())[0]
        assert nwbfile.processing['behavior']['BehavioralTimeSeries'].time_series[sample_beh_key].data.shape[0]>0
        #test stimulus:
        assert len(nwbfile.stimulus.keys()) > 0
        sample_stim_key = list(nwbfile.stimulus.keys())[0]
        assert nwbfile.stimulus[sample_stim_key].data.shape[0]>0
