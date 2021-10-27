# MT-Teql-artifact

Artifact of our paper "MT-Teql: Evaluating and Augmenting Neural NLIDB on Real-world Linguistic 
and Schema Variations" (VLDB’22). The code is tested with Python 3.6. The 
dependencies can be installed with the following command.

```shell
pip install -r requirements.txt
```


## Data Preparation

1. download Spider dataset from [https://yale-lily.github.io/spider](https://yale-lily.github.io/spider)
2. place ```train_spider.json```, ```dev.json``` and ```tables.json``` under ```data``` folder.

## Augmented Dataset, Pretrained Model Weight File and Experimental Data

Please refer to [http://bit.ly/MT-Teql-data](http://bit.ly/MT-Teql-data). We released all data to 
reproduce our experiments.

## Generate Mutations

Adjust the path in ```trans.py```, and run the following command.

```shell
python trans.py
```

you may wish to download pre-generated synthetic data from our supplementary material
and unzip ```mutation.zip``` to ```mutation/```.

## Test Models

In general, you need to adjust the data reader modules provided by different model 
implementations for testing models. We provided two sample test result of standard
[IRNet](https://github.com/microsoft/IRNet) and augmented IRNet models in 
```result/irnet-base.txt``` and ```result/irnet-as.txt``` for reproducing our result. 
You can run the following command.

```shell
python metamorphic_evaluation.py -t mutation/dev-tables.json -o result/irnet-base.txt
```

The script will output a list of metrics we used in our paper.

## Model Augmentation

You can use the provided training data to further augment any models which is compatible
to the standard Spider dataset. We also provide the augmented IRNet model 
(in ```model/irnet-as.model```) and corresponding testing result (in 
```result/irnet-as.txt```) for comparison. You can follow the official instruction 
of IRNet to evaluate the augmented model.
