import copy
import logging
import os
from typing import List
import torch

from src.experiments.base import BaseExperiment, BaseExperimentCV
from src.helper.data import DataHandler, DataHandlerCV
from src.utils.torch.data import (
    init_image_dataset,
    init_profile_dataset,
    init_multi_image_dataset,
)
from src.utils.torch.evaluation import (
    visualize_latent_space_pca_walk,
    save_latents_to_hdf,
)
from src.utils.torch.exp import model_train_val_test_loop
from src.utils.torch.general import get_device
from src.utils.torch.model import (
    get_domain_configuration,
    get_image_net_transformations_dict,
    get_image_net_nonrandom_transformations_dict,
    get_imagenet_extended_transformations_dict,
    get_randomflips_transformation_dict,
)


class BaseImageEmbeddingExperiment:
    def __init__(
        self,
        data_config: dict,
        model_config: dict,
        domain_name: str,
        save_freq: int = -1,
        pseudo_rgb: bool = False,
    ):

        self.data_transform_pipeline_dict = None
        self.data_loader_dict = None
        self.data_set = None
        self.data_key = None
        self.label_key = None
        self.extra_feature_key = None
        self.index_key = None
        self.domain_config = None
        self.data_config = data_config
        self.model_config = model_config
        self.domain_name = domain_name
        self.save_freq = save_freq
        self.pseudo_rgb = pseudo_rgb

    def initialize_image_data_set(self, multi_image: bool = False):
        self.data_key = self.data_config.pop("data_key")
        self.label_key = self.data_config.pop("label_key")
        if (
            "extra_features" in self.data_config
            and len(self.data_config["extra_features"]) > 0
        ):
            self.extra_feature_key = "extra_features"
        if "index_key" in self.data_config:
            self.index_key = self.data_config.pop("index_key")

        if multi_image:
            self.data_set = init_multi_image_dataset(**self.data_config)
        else:
            self.data_set = init_image_dataset(**self.data_config)

    def initialize_profile_data_set(self):
        self.data_key = self.data_config.pop("data_key")
        self.label_key = self.data_config.pop("label_key")
        if "index_key" in self.data_config:
            self.index_key = self.data_config.pop("index_key")
        if "extra_feature_key" in self.data_config:
            self.extra_feature_key = self.data_config.pop("extra_feature_key")

        self.data_set = init_profile_dataset(**self.data_config)

    def initialize_data_transform_pipeline(self, data_transform_pipeline: str = None):
        if data_transform_pipeline is None:
            self.data_transform_pipeline_dict = None
        elif data_transform_pipeline == "imagenet_random":
            self.data_transform_pipeline_dict = get_image_net_transformations_dict(224)
        elif data_transform_pipeline == "imagenet_nonrandom":
            self.data_transform_pipeline_dict = get_image_net_nonrandom_transformations_dict(
                224
            )
        elif data_transform_pipeline == "imagenet_extended_random":
            self.data_transform_pipeline_dict = get_imagenet_extended_transformations_dict(
                224
            )
        elif data_transform_pipeline == "randomflips":
            self.data_transform_pipeline_dict = get_randomflips_transformation_dict()

    def initialize_domain_config(self):
        model_config = self.model_config["model_config"]
        optimizer_config = self.model_config["optimizer_config"]
        loss_config = self.model_config["loss_config"]
        if self.label_weights is not None:
            loss_config["weight"] = self.label_weights

        self.domain_config = get_domain_configuration(
            name=self.domain_name,
            model_dict=model_config,
            data_loader_dict=None,
            data_key=self.data_key,
            label_key=self.label_key,
            index_key=self.index_key,
            extra_feature_key=self.extra_feature_key,
            optimizer_dict=optimizer_config,
            loss_fct_dict=loss_config,
        )

    def load_model(self, weights_fname):
        weights = torch.load(weights_fname)
        self.domain_config.domain_model_config.model.load_state_dict(weights)

    def extract_and_save_latents(self, output_dir):
        device = get_device()
        for dataset_type in ["val", "test"]:
            save_path = os.path.join(
                output_dir, "{}_latents.h5".format(str(dataset_type))
            )
            save_latents_to_hdf(
                domain_config=self.domain_config,
                save_path=save_path,
                dataset_type=dataset_type,
                device=device,
            )
        # save_path = os.path.join(output_dir, "all_latents.h5")
        # save_latents_to_hdf(
        #    domain_config=self.domain_config,
        #    save_path=save_path,
        #    dataset=self.data_set,
        #    device=device,
        # )


class ImageEmbeddingExperimentCV(BaseExperimentCV, BaseImageEmbeddingExperiment):
    def __init__(
        self,
        output_dir: str,
        data_config: dict,
        model_config: dict,
        domain_name: str,
        n_folds: int = 4,
        train_val_split: List = [0.8, 0.2],
        batch_size: int = 64,
        num_epochs: int = 500,
        early_stopping: int = 20,
        random_state: int = 42,
        save_freq=-1,
        pseudo_rgb: bool = False,
    ):
        BaseExperimentCV.__init__(
            self,
            output_dir=output_dir,
            n_folds=n_folds,
            train_val_split=train_val_split,
            batch_size=batch_size,
            num_epochs=num_epochs,
            early_stopping=early_stopping,
            random_state=random_state,
        )
        BaseImageEmbeddingExperiment.__init__(
            self,
            data_config=data_config,
            model_config=model_config,
            domain_name=domain_name,
            save_freq=save_freq,
            pseudo_rgb=pseudo_rgb,
        )
        self.trained_model_weights = None

    def initialize_image_data_set(self, multi_image: bool = False):
        super().initialize_image_data_set(multi_image=multi_image)

    def initialize_profile_data_set(self):
        super().initialize_profile_data_set()

    def initialize_domain_config(self):
        super().initialize_domain_config()

    def initialize_data_transform_pipeline(self, data_transform_pipeline: str = None):
        super().initialize_data_transform_pipeline(data_transform_pipeline)

    def initialize_data_loader_dict(
        self, drop_last_batch: bool = False,
    ):
        dh = DataHandlerCV(
            dataset=self.data_set,
            n_folds=self.n_folds,
            batch_size=self.batch_size,
            num_workers=5,
            random_state=self.random_state,
            transformation_dict=self.data_transform_pipeline_dict,
            drop_last_batch=drop_last_batch,
        )
        dh.stratified_kfold_split()
        dh.get_data_loader_dicts(shuffle=True)
        self.data_loader_dicts = dh.data_loader_dicts
        self.label_weights = dh.dataset.label_weights
        self.dataset = dh.dataset

    def train_models(self,):
        self.loss_dicts = []
        self.best_loss_dicts = []
        initial_model_weights = copy.deepcopy(
            self.domain_config.domain_model_config.model.state_dict()
        )

        for i in range(self.n_folds):
            self.fold_output_dir = os.path.join(
                self.output_dir, "fold_{}".format(i + 1)
            )
            os.makedirs(self.fold_output_dir)

            logging.debug("Start processing fold {}/{}".format(i + 1, self.n_folds))

            self.domain_config.data_loader_dict = self.data_loader_dicts[i]
            self.domain_config.domain_model_config.model.load_state_dict(
                initial_model_weights
            )

            trained_model, loss_dict, best_loss_dict = model_train_val_test_loop(
                output_dir=self.fold_output_dir,
                domain_config=self.domain_config,
                num_epochs=self.num_epochs,
                early_stopping=self.early_stopping,
                device=self.device,
                save_freq=self.save_freq,
            )
            self.loss_dicts.append(loss_dict)
            self.best_loss_dicts.append(best_loss_dict)
            self.visualize_loss_evolution(idx=i)
            super().extract_and_save_latents(output_dir=self.fold_output_dir)

    def evaluate_cv_performance(self):
        super().evaluate_cv_performance()


class ImageEmbeddingExperiment(BaseExperiment, BaseImageEmbeddingExperiment):
    def __init__(
        self,
        output_dir: str,
        data_config: dict,
        model_config: dict,
        domain_name: str,
        train_val_test_split: List[float] = [0.7, 0.2, 0.1],
        batch_size: int = 64,
        num_epochs: int = 64,
        early_stopping: int = -1,
        random_state: int = 42,
        save_freq: int = -1,
        pseudo_rgb: bool = False,
    ):
        BaseExperiment.__init__(
            self,
            output_dir=output_dir,
            train_val_test_split=train_val_test_split,
            batch_size=batch_size,
            num_epochs=num_epochs,
            early_stopping=early_stopping,
            random_state=random_state,
        )
        BaseImageEmbeddingExperiment.__init__(
            self,
            data_config=data_config,
            model_config=model_config,
            domain_name=domain_name,
            save_freq=save_freq,
            pseudo_rgb=pseudo_rgb,
        )

        self.trained_model = None
        self.loss_dict = None
        self.label_weights = None

    def initialize_image_data_set(self, multi_image: bool = False):
        super().initialize_image_data_set(multi_image=multi_image)

    def initialize_profile_data_set(self):
        super().initialize_profile_data_set()

    def initialize_data_transform_pipeline(self, data_transform_pipeline: str = None):
        super().initialize_data_transform_pipeline(
            data_transform_pipeline=data_transform_pipeline
        )

    def initialize_data_loader_dict(self, drop_last_batch: bool = False):

        dh = DataHandler(
            dataset=self.data_set,
            batch_size=self.batch_size,
            num_workers=5,
            random_state=self.random_state,
            transformation_dict=self.data_transform_pipeline_dict,
            drop_last_batch=drop_last_batch,
        )
        dh.stratified_train_val_test_split(splits=self.train_val_test_split)
        dh.get_data_loader_dict(shuffle=True)
        self.data_loader_dict = dh.data_loader_dict
        self.label_weights = dh.dataset.label_weights
        self.data_set = dh.dataset

    def initialize_domain_config(self):
        super().initialize_domain_config()

    def train_models(self):
        self.domain_config.data_loader_dict = self.data_loader_dict
        (
            self.trained_model,
            self.loss_dict,
            self.best_loss_dict,
        ) = model_train_val_test_loop(
            output_dir=self.output_dir,
            domain_config=self.domain_config,
            num_epochs=self.num_epochs,
            early_stopping=self.early_stopping,
            device=self.device,
            save_freq=self.save_freq,
        )

    def load_model(self, weights_fname):
        super().load_model(weights_fname=weights_fname)

    def extract_and_save_latents(self):
        super().extract_and_save_latents(output_dir=self.output_dir)

    def visualize_loss_evolution(self):
        super().visualize_loss_evolution()

    def visualize_latent_space_pca_walk(
        self, dataset_type: str = "test", n_components: int = 2, n_steps: int = 11
    ):
        output_dir = os.path.join(self.output_dir, "pc_latent_walk")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if self.domain_config.domain_model_config.classifier.model_base_type not in [
            "ae",
            "vae",
        ]:
            raise RuntimeError("Only implemented for autoencoder models")
        else:
            visualize_latent_space_pca_walk(
                domain_config=self.domain_config,
                output_dir=output_dir,
                dataset_type=dataset_type,
                n_components=n_components,
                n_steps=n_steps,
            )

    def evaluate_test_performance(self):
        super().evaluate_test_performance()