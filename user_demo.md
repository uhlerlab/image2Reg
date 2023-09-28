# Demo application using user-provided image inputs

## Overview

This version of our demo application applies our Image2Reg pipeline to input images provided by the user. In particular, our pipeline outputs a prediction of the genes that were overexpressed in the cells in the input images. Thus, this version shows how our Image2Reg pipeline can be applied to new image data sets. 

> [!NOTE]
> We recommend running this variant only after you have first run the demo using the test input images which is described [here](test_demo.md).

---

<!--
## Perequisites
To run our pipeline, you will need provide two different image inputs.

### Raw chromatin images
Field-of-view chromatin images of cells are required as input for our pipeline. These images are expected to be black-and-white (i.e. single-channel) images and each pixel is assigned unsigned integer value.
All images need have a unique file name and be located in the same directory. Example images from the image data set of [Rohban et al. (2017)](https://doi.org/10.7554/eLife.24060) are downloaded the first time our demo application is run and are then e.g. located in the directory ``test_data/sample_data/JUN/raw``.

> [!NOTE]
> Our pipeline was set up using 20x resolution 1080x1080px images of U2OS cells. If your input images are of very different resolution and/or your cells are of different size, the default parameters of the pipeline might lead no nuclei being detected. Please refer to the entry *No or just one nuclei is found* in our [Troubleshooting section](README.md#Troubleshooting/Support) for guidance on how to adjust the paramters.

### Nuclear mask images
For each field-of-view chromatin image a corresponding nuclear segmentation mask is required. These mask images are expected to be black-and-white (i.e. single-channel) images where all pixels that form the mask of the same nucleus are assigned the same unsigned integer value.
The background is assigned a value of 0. Each nuclear mask image must have exactly the same file name as the corresponding chromatin image and all nuclear mask images need to be located in the same directory. Example nuclear segmentation masks for the respective example images from the data set from [Rohban et al. (2017)](https://doi.org/10.7554/eLife.24060) are downloaded alongside the chromatin images the first time our demo application is run and are then e.g. located in the directory ``test_data/sample_data/JUN/unet_masks``.


#
-->

## Step-by-step guide

> [!IMPORTANT]
> Before you proceed make sure that you have followed the instructions in the [README file](https://github.com/uhlerlab/image2reg/blob/master/README.md) of this repository. In particular, ensure that you have run the steps 1 and 2 of the [Step-by-Step guide provided in the README file](https://github.com/uhlerlab/image2reg/blob/master/README.md#step-by-step-guide).
> To run the code please ensure that your working directory is ``image2reg``. The working directory can be changed via the ``cd`` command.

### 1. Activating the bash shell
Please open a new terminal and activate the bash shell via
```
bash
```

### 2. Set image2reg as your working directory
Please navigate to the location where you cloned the github repository to.
If you have exactly followed the instructions provided in the [README file](https://github.com/uhlerlab/image2reg/blob/master/README.md), this can be done via typing

```
cd ~/image2reg
```
 in the terminal.

 #

 ### 3. Running the demo application 

Our demo can be run in the terminal via

 ```
source scripts/demo/image2reg_demo_new_data.sh --image_dir /path/to/input/raw/chromatin/images --mask_dir /path/to/nuclear/segmentation/masks
```
where you 
- replace the ``/path/to/input/raw/chromatin/images`` with the directory that contains the chromatin images you would like to apply our pipeline to, e.g. ``test_data/sample_data/JUN/raw``
- replace the ``/path/to/nuclear/segmentation/masks`` with the directory that contains the corresponding segmentation masks, e.g. ``test_data/sample_data/JUN/unet_masks``

The above command will run the complete demo. 
**No further user-interaction will be required.**
Please refer to the following section for more information on the triggered processes.

While you can use your own imaging data, we also provide the sample imaging data for 10 distinct overexpression conditions from the data set from [Rohban et al. (2017)](https://doi.org/10.7554/eLife.24060) that the user can provide as input to test our demo.

<details>
  <summary>
    <b>Click here if you want to use the provided sample image data</b>
  </summary>

| Overexpression condition | Command | 
| --- | --- |
| **BRAF** | ``source scripts/demo/image2reg_demo_new_data.sh --image_dir test_data/sample_data/BRAF/raw --mask_dir test_data/sample_data/BRAF/unet_masks`` |
| **CEBPA** | ``source scripts/demo/image2reg_demo_new_data.sh --image_dir test_data/sample_data/CEBPA/raw --mask_dir test_data/sample_data/CEBPA/unet_masks`` |
| **CREB1** | ``source scripts/demo/image2reg_demo_new_data.sh --image_dir test_data/sample_data/CREB1/raw --mask_dir test_data/sample_data/CREB1/unet_masks`` |
| **JUN** | ``source scripts/demo/image2reg_demo_new_data.sh --image_dir test_data/sample_data/JUN/raw --mask_dir test_data/sample_data/JUN/unet_masks`` |
| **PRKCE** | ``source scripts/demo/image2reg_demo_new_data.sh --image_dir test_data/sample_data/PRKCE/raw --mask_dir test_data/sample_data/PRKCE/unet_masks`` |
| **RAF1** | ``source scripts/demo/image2reg_demo_new_data.sh --image_dir test_data/sample_data/RAF1/raw --mask_dir test_data/sample_data/RAF1/unet_masks`` |
| **RELB** | ``source scripts/demo/image2reg_demo_new_data.sh --image_dir test_data/sample_data/RELB/raw --mask_dir test_data/sample_data/RELB/unet_masks`` |
| **RHOA**| ``source scripts/demo/image2reg_demo_new_data.sh --image_dir test_data/sample_data/RHOA/raw --mask_dir test_data/sample_data/RHOA/unet_masks`` |
| **SMAD4** | ``source scripts/demo/image2reg_demo_new_data.sh --image_dir test_data/sample_data/SMAD4/raw --mask_dir test_data/sample_data/SMAD4/unet_masks`` |
| **SREBF1** | ``source scripts/demo/image2reg_demo_new_data.sh --image_dir test_data/sample_data/SREBF1/raw --mask_dir test_data/sample_data/SREBF1/unet_masks`` |
  
</details>

<details>
 <summary>
  <b>Click here if you want to use your own image data</b> </summary>
 
  To run our pipeline, you will need provide two different image inputs.
  
  ### Raw chromatin images
  Field-of-view chromatin images of cells are required as input for our pipeline. These images are expected to be black-and-white (i.e. single-channel) images. In these images each pixel is assigned unsigned integer value.
  All images need have a unique file name and need to be located in the same directory. Example images from the image data set of [Rohban et al. (2017)](https://doi.org/10.7554/eLife.24060) are downloaded the first time our demo application is run. Once it has been run, you can find
  example images from the JUN overexpression condition in the directory ``test_data/sample_data/JUN/raw``.
  
  > [!NOTE]
  > Our pipeline was set up using 20x resolution 1080x1080px images of U2OS cells. If your input images are of very different resolution and/or your cells are of different size, the default parameters of the pipeline might lead no nuclei being detected. Please refer to the entry *No or just one nuclei is found* in our [Troubleshooting section](README.md#Troubleshooting/Support) for guidance on how to adjust the paramters.

  ### Nuclear mask images
  For each field-of-view chromatin image a corresponding nuclear segmentation mask is required. These mask images are expected to be black-and-white (i.e. single-channel) images. In each image all pixels that jointly form the mask of the same nucleus are assigned the same unsigned      integer value.
  The background is assigned a value of 0. Each nuclear mask image must have exactly the same file name as the corresponding chromatin image.  All nuclear mask images need to be located in the same directory. Example nuclear segmentation masks for the respective example images from the data set from [Rohban et al. (2017)](https://doi.org/10.7554/eLife.24060) are downloaded alongside the chromatin images the first time our demo application is run and are then e.g. located in the directory ``test_data/sample_data/JUN/unet_masks``.

</details>


#

### *4. Advanced run settings/developer options (Optional)*
Our demo application can also be run with two additional optional arguments.
1. ``--environment``:    This argument can be used if one would like to specify a pre-existing conda environment that is supposed to be used to run the demo application. By default, if the argument is not provided a new conda environment will be setup as part of the demo application called ``image2reg_demo`` in which all required python packages will be installed and that is used to run our code.
2. ``--help``:    This argument can be used to obtain help on the usage of our demo

For example, if you have run the test version of our demo application (described here) before, you can re-use the ``image2reg_demo`` conda environment that had been installed via:
```
source scripts/demo/image2reg_demo_new_data.sh --environment image2reg image2reg_demo --image_dir /path/to/input/raw/chromatin/images --mask_dir /path/to/nuclear/segmentation/masks
```

---

## Processes triggered by the demo application

### Demo preparation
1. A new conda environment called ``image2reg_demo`` is installed that contains all software packages required to run the code.
2. A directory called ``test_data`` is downloaded from the [DOI 10.5281/zenodo.8354979](https://doi.org/10.5281/zenodo.8354979) and extracted within the image2reg repository. This step is skipped if such a directory already exists. This should only be the case, if you have run the demo application successfully before.
3. The input images you provide will be copied in the designated directories, i.e. the chromatin images are copied to ``test_data/UNKNOWN/images/raw/plate`` and the segmentation masks are copied to ``test_data/UNKNOWN/images/raw/plate``.

> [!WARNING]
> Please do not interrupt the download of the data directories and their extraction, i.e. unzipping. This could result in corrupt files which will break the demo application. If you encounter any problems indicating that some files were not found, please remove the ``test_data`` and if existing the ``demo`` directory located in the cloned image2reg repository. Once you have removed these directories please restart the demo as described in above. If any issues persist, please consult the Troubleshooting section below.

>[!WARNING] 
> All contents in the directories ``test_data/UNKNOWN/images/raw/plate`` and ``test_data/UNKNOWN/images/unet_masks/plate`` are deleted before the new data is copied.

#

### Application of our Image2Reg
 
Next, the demo performs the following inference steps for the provided input images and output the 10 genes that were most likely overexpressed in the cells captured in the data set (in decreasing order).

1. Preprocess the chromatin images provided by the user for which the pipeline should infer the perturbed gene.
2. Obtain the image and consequently the gene perturbation embedding for the input images by encoding the images using the pretrained convolutional neural network ensemble image encoder model.
3. Link the gene perturbation embeddings of their corresponding regulatory gene embeddings by training the kernel regression model.
4. Output the 10 genes most likely overexpressed (in decreasing order) in the cells in the input images.

---

## Troubleshooting

In case you run into any errors please also consult the following section and the [Troubleshooting section in our README file](README.md#Troubleshooting/Support).

