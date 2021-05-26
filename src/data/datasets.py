import logging
import os
from collections import Counter
from typing import List

import torch
import numpy as np
import pandas as pd
from PIL import Image
from imblearn.under_sampling import RandomUnderSampler
from sklearn.preprocessing import LabelEncoder
from torch import Tensor
from torch.utils.data import Dataset, Subset
from torchvision import transforms
from skimage.io import imread

from src.utils.basic.general import combine_path
from src.utils.basic.io import get_file_list


class LabeledDataset(Dataset):
    def __init__(self):
        super(LabeledDataset, self).__init__()
        self.labels = None
        self.transform_pipeline = None


class TorchNucleiImageDataset(LabeledDataset):
    def __init__(
        self,
        image_dir,
        metadata_file,
        image_file_col: str = "image_file",
        plate_col: str = "plate",
        label_col: str = "gene_symbol",
        target_list: List = None,
        n_control_samples: int = None,
        transform_pipeline: transforms.Compose = None,
        pseudo_rgb: bool = False,
    ):
        super().__init__()
        self.image_dir = image_dir
        self.metadata_file = metadata_file
        self.image_file_col = image_file_col
        self.plate_col = plate_col
        self.label_col = label_col
        self.metadata = pd.read_csv(self.metadata_file, index_col=0)
        if target_list is not None:
            if "EMPTY" not in target_list:
                target_list += ["EMPTY"]
            self.metadata = self.metadata.loc[
                self.metadata[label_col].isin(target_list), :
            ]
        if n_control_samples is not None:
            idc = np.array(list(range(len(self.metadata)))).reshape(-1, 1)
            labels = self.metadata[self.label_col]
            target_n_samples = dict(Counter(labels))
            target_n_samples["EMPTY"] = n_control_samples
            idc, _ = RandomUnderSampler(
                sampling_strategy=target_n_samples, random_state=1234
            ).fit_resample(idc, labels)
            self.metadata = self.metadata.iloc[idc.flatten(), :]
            logging.debug(
                "Label counts after undersampling: %s",
                dict(Counter(np.array(self.metadata[self.label_col]))),
            )

        # Numpy data type problem leads to strings being cutoff when applying along axis
        self.image_locs = np.apply_along_axis(
            combine_path,
            0,
            [
                np.repeat(image_dir, len(self.metadata)).astype(str),
                np.array(self.metadata.loc[:, self.plate_col], dtype=str),
                np.array(self.metadata.loc[:, self.image_file_col], dtype=str),
            ],
        ).astype(object)

        if len(self.metadata) != len(self.image_locs):
            raise RuntimeError(
                "Number of image samples does not match the given metadata."
            )
        self.labels = np.array(self.metadata.loc[:, label_col])
        le = LabelEncoder().fit(self.labels)
        self.labels = le.transform(self.labels)
        le_name_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
        logging.debug("Classes are coded as follows: %s", le_name_mapping)
        self.set_transform_pipeline(transform_pipeline)
        self.pseudo_rgb = pseudo_rgb

    def __len__(self):
        return len(self.image_locs)

    def __getitem__(self, idx):
        image_loc = self.image_locs[idx]
        image = self.process_image(image_loc)
        gene_label = self.labels[idx]

        sample = {"id": image_loc, "image": image, "label": gene_label}
        return sample

    def set_transform_pipeline(
        self, transform_pipeline: transforms.Compose = None
    ) -> None:
        if transform_pipeline is None:
            self.transform_pipeline = transforms.Compose([transforms.ToTensor()])
        else:
            self.transform_pipeline = transform_pipeline

    def process_image(self, image_loc: str) -> Tensor:
        image = imread(image_loc)
        image = Image.fromarray(image)
        if self.pseudo_rgb:
            rgbimg = Image.new("RGB", image.size)
            rgbimg.paste(image)
            image = rgbimg
        # image = np.array(image, dtype=np.float32)
        # image = (image - image.min()) / (image.max() - image.min())
        # image = np.clip(image, 0, 1)
        # image = torch.from_numpy(image).unsqueeze(0)
        image = self.transform_pipeline(image)
        return image


class TorchTransformableSubset(Subset):
    def __init__(self, dataset: LabeledDataset, indices):
        super().__init__(dataset=dataset, indices=indices)
        self.transform_pipeline = None

    def set_transform_pipeline(self, transform_pipeline: transforms.Compose) -> None:
        try:
            #todo change not only on subset but for the whole data set - undesired
            #self.transform_pipeline = transform_pipeline
            self.dataset.set_transform_pipeline(transform_pipeline)
        except AttributeError as exception:
            logging.error(
                "Object must implement a subset of a dataset type that implements the "
                "set_transform_pipeline method."
            )
            raise exception
