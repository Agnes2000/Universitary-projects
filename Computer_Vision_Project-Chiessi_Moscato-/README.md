# **PREDICTION OF GRASP POSITIONS FOR CUBIC OBJECTS IN IMAGES**

This repository contains the code and dataset for the project "Prediction of Grasp Positions for Cubic Objects in Images".  
The goal of this project is to create a dataset of cubic objects, predict the correct grasp positions using the computation of the
center of mass, train a linear regression Convolutional Neural Network (CNN) model, and finally, input new images to calculate grasp positions with the trained model.

## **Dataset Creation**

The dataset consists of images of cubic objects. For each image:
- The correct grasp positions are computed based on the center of mass of the objects
- The dataset is labeled with the computed grasp coordinates, distance from the center of mass and evaluation of the grasp.

![ Image loaded ](Images/Cubo_giallo.png)

To create the dataset, the following steps were followed:
- Image loading: cube creation, cube upload and mask computation
- Creation of evaluation table: grasp position generation and label assignment
- Data augmentation: tranformations applied to the dataset.

![Grasp position generation and center of mass](Images/grasp_positions_and_center_of_mass.png)

## **Model training**

The model used for grasp position prediction is a linear regression Convolutional Neural Network (CNN). The key steps in model training include:  
- Data preparation: train and test division
- Model: definition and compilation
- Training: optimizing the model to minimize the error in predicting the grasp coordinates.

## **Grasp Position Prediction**

After training the model, it can be used to predict the grasp positions for new images of cubic objects. The input image is fed into the model, which outputs the predicted grasp coordinates  
and also an image that allows to visualize the output.

![Best grasp position generated](Images/best_grasp_position.png)
