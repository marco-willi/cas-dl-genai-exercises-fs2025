"""Generic Image Folder Dataset"""
from pathlib import Path
from typing import Callable

import lightning as L
import numpy as np
from PIL import Image
from torch.utils.data import DataLoader, Dataset

from .. import utils


class ImageFolder(Dataset):
    """Create Dataset from class specific folders."""

    def __init__(
        self,
        root_path: str | Path,
        transform: Callable | None = None,
    ):
        """
        Args:
            root_path: Path to directory that contains the class-specific folders
            transform: Optional transform to be applied on an image
            classes: List of class names.
        """
        self.root_path = root_path
        self.observations = utils.find_all_imges_and_their_labels(root_path)
        self.transform = transform
        self.classes = sorted({x["label"] for x in self.observations})
        print(
            f"Found the following classes: {self.classes}, in total {len(self.observations)} images"
        )

    def __len__(self):
        return len(self.observations)

    def __getitem__(self, idx: int):
        image_path = self.observations[idx]["image_path"]
        image = Image.open(image_path)
        label = self.observations[idx]["label"]
        label_num = self.classes.index(label)

        if self.transform:
            image = self.transform(image)
        return {"image": image, "label": label_num}

    @classmethod
    def from_subset(
        cls, original_dataset, subset_indices: list[int], transform: Callable | None = None
    ):
        """
        Create a subset of the original dataset with only the specified indices.

        Args:
            original_dataset (ImageFolder): An instance of the ImageFolder dataset.
            subset_indices (List[int]): List of indices to create a subset of observations.
            transform: Override transform of current ds

        Returns:
            ImageFolder: A new instance of ImageFolder with the subset observations.
        """
        # Create a new instance with the same properties as the original
        subset_instance = cls(
            root_path=original_dataset.root_path,
            transform=original_dataset.transform if transform is None else transform,
        )

        # Filter the observations based on the subset indices
        subset_instance.observations = [original_dataset.observations[i] for i in subset_indices]
        subset_instance.classes = original_dataset.classes  # Keep class list consistent

        print(
            f"Created a subset with {len(subset_instance.observations)} images "
            f"from the original dataset of {len(original_dataset.observations)} images"
        )

        return subset_instance


class ImageFolderRandom(ImageFolder):
    """Modify parent class to return random image."""

    def __getitem__(self, idx: int):
        image_path = self.observations[idx]["image_path"]
        image = Image.open(image_path)
        label = self.observations[idx]["label"]
        label_num = self.classes.index(label)

        random_image = Image.fromarray(np.random.randint(0, 256, image.size, dtype=np.uint8))

        if self.transform:
            random_image = self.transform(random_image)
        return {"image": random_image, "label": label_num}


class DataSetModule(L.LightningDataModule):
    """Create a data module to manage train, validation and test sets."""

    def __init__(
        self,
        ds_train: Dataset,
        ds_val: Dataset,
        ds_test: Dataset,
        classes: list[str],
        train_transform: Callable | None,
        test_transform: Callable | None,
        batch_size: int = 32,
        num_workers: int = 4,
    ):
        super().__init__()
        self.classes = classes
        self.batch_size = batch_size
        self.num_workers = num_workers

        self.ds_train = ds_train
        self.ds_val = ds_val
        self.ds_test = ds_test
        self.train_transform = train_transform
        self.test_transform = test_transform

    def setup(self, stage=None):
        """Split the dataset into train, validation, and test sets."""
        if stage == "fit" or stage is None:
            if self.train_transform is not None:
                self.ds_train.transform = self.train_transform
            if self.test_transform is not None:
                self.ds_val.transform = self.test_transform

        if stage == "test" or stage is None:
            if self.test_transform is not None:
                self.ds_test.transform = self.test_transform

    def train_dataloader(self):
        """Return the train data loader."""
        return DataLoader(
            self.ds_train, batch_size=self.batch_size, shuffle=True, num_workers=self.num_workers
        )

    def val_dataloader(self):
        """Return the validation data loader."""
        return DataLoader(
            self.ds_val, batch_size=self.batch_size, shuffle=False, num_workers=self.num_workers
        )

    def test_dataloader(self):
        """Return the test data loader."""
        return DataLoader(
            self.ds_test, batch_size=self.batch_size, shuffle=False, num_workers=self.num_workers
        )
