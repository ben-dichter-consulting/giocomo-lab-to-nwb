import json
import uuid
import warnings
from datetime import datetime
from pathlib import Path

import jsonschema
from nwb_conversion_tools import NWBConverter, SbxImagingInterface, Suite2pSegmentationInterface
from nwb_conversion_tools.json_schema_utils import dict_deep_update
from pytz import timezone

from .giocomovrdatainterface import GiocomoVRInterface


class GiocomoImagingInterface(NWBConverter):
    data_interface_classes = dict(
        SbxImagingInterface=SbxImagingInterface,
        Suite2pSegmentationInterface=Suite2pSegmentationInterface,
        GiocomoVRInterface=GiocomoVRInterface
    )

    def __init__(self, source_data: [dict, str]):
        """
        Converts acquisition images from scanbox, segmentation data after Suite2p and behavioral VR
        data from pickled dataframes.
        Parameters
        ----------
        source_data : str
            path to the .mat/sbx file
        """
        if isinstance(source_data, dict):
            jsonschema.validate(source_data, self.get_source_schema())
            source_data_dict = source_data
        else:
            source_data = Path(source_data)
            assert source_data.suffix in ['.mat', '.sbx'], 'source_data should be path to .mat/.sbx file'
            source_data_dict = dict(
                SbxImagingInterface=dict(file_path=str(source_data))
            )
            s2p_folder = source_data.with_suffix('')/'suite2p'
            if not s2p_folder.exists():
                warnings.warn('could not find suite2p')
            else:
                source_data_dict.update(Suite2pSegmentationInterface=dict(file_path=str(s2p_folder)))
            pkl_file = source_data.with_suffix('.pkl')
            if not pkl_file.exists():
                pkl_file = \
                    source_data.parents[3]/'VR_pd_pickles'/source_data.relative_to(source_data.parents[3]).with_suffix(
                        '.pkl')
                if not pkl_file.exists():
                    warnings.warn('could not find .pkl file')
                else:
                    source_data_dict.update(GiocomoVRInterface=dict(file_path=str(pkl_file)))
            else:
                source_data_dict.update(GiocomoVRInterface=dict(file_path=str(pkl_file)))
        self.source_data_dict = source_data_dict
        super().__init__(source_data_dict)

    def get_metadata(self):
        metadata_out = super().get_metadata()
        file_path = Path(list(self.source_data_dict.values())[0]['file_path'])
        exp_desc = file_path.parents[0].name
        date = file_path.parents[1].name
        time_zone = timezone('US/Pacific')
        subject_num = file_path.parents[2].name
        session_desc = file_path.stem
        subject_info_path = Path(__file__).parent/'subjectdata.json'
        with open(str(subject_info_path), 'r') as js:
            all_sub_details = json.load(js)
        subject_details = all_sub_details[subject_num]
        metadata = dict(
            NWBFile=dict(
                session_description=session_desc,
                identifier=str(uuid.uuid4()),
                session_start_time=datetime.strptime(date, "%d_%m_%Y").astimezone(time_zone),
                experiment_description=exp_desc,
                virus=f'virus injection date: {subject_details["virus injection date"]}, '
                      f'virus: {subject_details["VIRUS"]}',
                surgery=f'cannula implant date: {subject_details["cannula implant date"]}',
                lab='GiocomoLab',
                institution='Stanford University School of Medicine',
                experimenter='Mark Plitt'
            ),
            Subject=dict(
                subject_id=subject_details['ID'],
                species=subject_details['species'],
                date_of_birth=datetime.strptime(subject_details['DOB'], "%Y-%m-%d %H:%M:%S").astimezone(time_zone),
                genotype=subject_details['genotype'],
                sex=subject_details['sex'],
                weight=subject_details['weight at time of implant']
            )
        )
        return dict_deep_update(metadata_out, metadata)
