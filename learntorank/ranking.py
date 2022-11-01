# AUTOGENERATED! DO NOT EDIT! File to edit: ../004_module_ranking.ipynb.

# %% auto 0
__all__ = ['keras_linear_model', 'keras_lasso_linear_model', 'keras_ndcg_compiled_model', 'LinearHyperModel', 'LassoHyperModel',
           'ListwiseRankingFramework']

# %% ../004_module_ranking.ipynb 4
import json
import os
import os.path
from typing import Optional
import pandas as pd
import tensorflow as tf
import tensorflow_ranking as tfr
import keras_tuner as kt
from tensorflow.keras.layers import Normalization

# %% ../004_module_ranking.ipynb 5
def keras_linear_model(
    number_documents_per_query,  # Number of documents per query to reshape the listwise prediction.
    number_features,  # Number of features used per document.
) -> tf.keras.Sequential:  # The uncompiled Keras model.
    "linear model with a lasso constrain on the kernel weights."
    
    model = tf.keras.Sequential()
    model.add(
        tf.keras.layers.Input(shape=(number_documents_per_query, number_features))
    )
    model.add(
        tf.keras.layers.Dense(
            1,
            use_bias=False,
            activation=None,
        )
    )
    model.add(tf.keras.layers.Reshape((number_documents_per_query,)))
    return model


# %% ../004_module_ranking.ipynb 8
def keras_lasso_linear_model(
    number_documents_per_query,  # Number of documents per query to reshape the listwise prediction.
    number_features,  # Number of features used per document.
    l1_penalty,  # Controls the L1-norm penalty.
    normalization_layer: Optional=None,  # Initialized normalization layers. Used when performing feature selection.
) -> tf.keras.Sequential:  # The uncompiled Keras model.
    "linear model with a lasso constrain on the kernel weights."
    
    model = tf.keras.Sequential()
    model.add(
        tf.keras.layers.Input(shape=(number_documents_per_query, number_features))
    )
    if normalization_layer:
        model.add(normalization_layer)
    model.add(
        tf.keras.layers.Dense(
            1,
            use_bias=False,
            activation=None,
            kernel_regularizer=tf.keras.regularizers.L1(l1_penalty),
        )
    )
    model.add(tf.keras.layers.Reshape((number_documents_per_query,)))
    return model

# %% ../004_module_ranking.ipynb 11
def keras_ndcg_compiled_model(
    model,  # Uncompiled Keras model 
    learning_rate,  # Learning rate used in the Adagrad optim algo.
    top_n  # Top n used when computing the NDCG metric
):
    "Compile listwise Keras model with NDCG stateless metric and ApproxNDCGLoss"
    
    ndcg = tfr.keras.metrics.NDCGMetric(topn=top_n)

    def ndcg_stateless(y_true, y_pred):
        ndcg.reset_states()
        return ndcg(y_true, y_pred)

    optimizer = tf.keras.optimizers.Adagrad(learning_rate)
    model.compile(
        optimizer=optimizer,
        loss=tfr.keras.losses.ApproxNDCGLoss(),
        metrics=ndcg_stateless,
    )
    return model

# %% ../004_module_ranking.ipynb 14
class LinearHyperModel(kt.HyperModel):
    """
    Define a KerasTuner search space for linear models
    """          
    def __init__(
        self,
        number_documents_per_query,
        number_features,
        top_n=10,
        learning_rate_range=None,
    ):
        self.number_documents_per_query = number_documents_per_query
        self.number_features = number_features
        self.top_n = top_n
        if not learning_rate_range:
            learning_rate_range = [1e-2, 1e2]
        self.learning_rate_range = learning_rate_range
        super().__init__()


    def build(self, hp):
        model = keras_linear_model(
            number_documents_per_query=self.number_documents_per_query,
            number_features=self.number_features,
        )
        compiled_model = keras_ndcg_compiled_model(
            model=model,
            learning_rate=hp.Float(
                "learning_rate",
                min_value=self.learning_rate_range[0],
                max_value=self.learning_rate_range[1],
                sampling="log",
            ),
            top_n=self.top_n,
        )
        return compiled_model

# %% ../004_module_ranking.ipynb 16
class LassoHyperModel(kt.HyperModel):
    """
    Define a KerasTuner search space for lasso models
    """              
    def __init__(
        self,
        number_documents_per_query,
        number_features,
        trained_normalization_layer,
        top_n=10,
        l1_penalty_range=None,
        learning_rate_range=None,
    ):
        self.number_documents_per_query = number_documents_per_query
        self.number_features = number_features
        self.trained_normalization_layer = trained_normalization_layer
        self.top_n = top_n
        if not l1_penalty_range:
            l1_penalty_range = [1e-4, 1e-2]
        self.l1_penalty_range = l1_penalty_range
        if not learning_rate_range:
            learning_rate_range = [1e-2, 1e2]
        self.learning_rate_range = learning_rate_range
        super().__init__()

    def build(self, hp):
        model = keras_lasso_linear_model(
            number_documents_per_query=self.number_documents_per_query,
            number_features=self.number_features,
            l1_penalty=hp.Float(
                "lambda",
                min_value=self.l1_penalty_range[0],
                max_value=self.l1_penalty_range[1],
                sampling="log",
            ),
            normalization_layer=self.trained_normalization_layer,
        )
        compiled_model = keras_ndcg_compiled_model(
            model=model,
            learning_rate=hp.Float(
                "learning_rate",
                min_value=self.learning_rate_range[0],
                max_value=self.learning_rate_range[1],
                sampling="log",
            ),
            top_n=self.top_n,
        )
        return compiled_model

# %% ../004_module_ranking.ipynb 17
class ListwiseRankingFramework:
    def __init__(
        self,
        number_documents_per_query,
        batch_size=32,
        shuffle_buffer_size=1000,
        tuner_max_trials=3,
        tuner_executions_per_trial=1,
        tuner_epochs=1,
        tuner_early_stop_patience=None,
        final_epochs=1,
        top_n=10,
        l1_penalty_range=None,
        learning_rate_range=None,
        folder_dir=os.getcwd(),
    ):
        "Listwise ranking framework"
        self.number_documents_per_query = number_documents_per_query
        self.batch_size = batch_size
        self.shuffle_buffer_size = shuffle_buffer_size
        self.tuner_max_trials = tuner_max_trials
        self.tuner_executions_per_trial = tuner_executions_per_trial
        self.tuner_epochs = tuner_epochs
        self.tuner_early_stop_patience = tuner_early_stop_patience
        self.final_epochs = final_epochs
        self.top_n = top_n
        self.l1_penalty_range = l1_penalty_range
        self.learning_rate_range = learning_rate_range
        self.folder_dir = folder_dir

        self.query_id_name = "query_id"
        self.target_name = "label"
        self.distribute_strategy = tf.distribute.MirroredStrategy()
        

    def listwise_tf_dataset_from_df(
        self, df, feature_names, shuffle_buffer_size, batch_size
    ):
        """
        Create TensorFlow dataframe suited for listwise loss function from pandas df.

        :param df: Pandas df containing the data.
        :param feature_names: Features to be used in the tensorflow model.
        :param shuffle_buffer_size: The size of the buffer used to sample data from.
        :param batch_size: The size of the batch for each sample from the dataset.
        :return: TF dataset
        """
        ds = tf.data.Dataset.from_tensor_slices(
            {
                "features": tf.cast(df[feature_names].values, tf.float32),
                "label": tf.cast(df[self.target_name].values, tf.float32),
                "query_id": tf.cast(df[self.query_id_name].values, tf.int64),
            }
        )

        key_func = lambda x: x[self.query_id_name]
        reduce_func = lambda key, dataset: dataset.batch(
            self.number_documents_per_query, drop_remainder=True
        )
        listwise_ds = ds.group_by_window(
            key_func=key_func,
            reduce_func=reduce_func,
            window_size=self.number_documents_per_query,
        )
        listwise_ds = listwise_ds.map(lambda x: (x["features"], x["label"]))
        listwise_ds = listwise_ds.shuffle(buffer_size=shuffle_buffer_size).batch(
            batch_size=batch_size
        )
        return listwise_ds

    def listwise_tf_dataset_from_csv(
        self, file_path, feature_names, shuffle_buffer_size, batch_size
    ):
        """
        Create TensorFlow dataframe suited for listwise loss function from a .csv file.

        :param file_path: The path to the csv file.
        :param feature_names: Features to be used in the tensorflow model.
        :param shuffle_buffer_size: The size of the buffer used to sample data from.
        :param batch_size: The size of the batch for each sample from the dataset.
        :return: TF dataset
        """
        ds = tf.data.experimental.make_csv_dataset(
            file_path,
            batch_size=1,
            num_epochs=1,
            shuffle_buffer_size=shuffle_buffer_size,
        )

        def create_dict_slices(x):
            return {
                "query_id": tf.reshape(tf.cast(x["query_id"], tf.int64), []),
                "label": tf.reshape(tf.cast(x["label"], tf.float32), []),
                "features": tf.cast(
                    tf.reshape(
                        [x[name] for name in feature_names], [len(feature_names)]
                    ),
                    tf.float32,
                ),
            }

        ds_mapped = ds.map(lambda x: create_dict_slices(x))
        key_func = lambda x: x[self.query_id_name]
        reduce_func = lambda key, dataset: dataset.batch(
            self.number_documents_per_query, drop_remainder=True
        )
        listwise_ds = ds_mapped.group_by_window(
            key_func=key_func,
            reduce_func=reduce_func,
            window_size=self.number_documents_per_query,
        )
        listwise_ds = listwise_ds.map(lambda x: (x["features"], x["label"]))
        listwise_ds = listwise_ds.batch(batch_size=batch_size)
        return listwise_ds

    def create_dataset(self, df_or_file, feature_names):
        if isinstance(df_or_file, pd.DataFrame):
            ds = self.listwise_tf_dataset_from_df(
                df=df_or_file,
                feature_names=feature_names,
                shuffle_buffer_size=self.shuffle_buffer_size,
                batch_size=self.batch_size,
            )
        else:
            ds = self.listwise_tf_dataset_from_csv(
                file_path=df_or_file,
                feature_names=feature_names,
                shuffle_buffer_size=self.shuffle_buffer_size,
                batch_size=self.batch_size,
            )
        return ds

    def create_and_train_normalization_layer(self, train_ds):
        normalization_layer = tf.keras.layers.Normalization()
        train_feature_ds = train_ds.map(lambda x, y: x)
        normalization_layer.adapt(train_feature_ds)
        return normalization_layer

    def tune_model(self, model, train_ds, dev_ds):
        tuner = kt.RandomSearch(
            model,
            objective=kt.Objective("val_ndcg_stateless", direction="max"),
            directory=self.folder_dir,
            project_name="keras_tuner",
            distribution_strategy=self.distribute_strategy,
            overwrite=True,
            max_trials=self.tuner_max_trials,
            executions_per_trial=self.tuner_executions_per_trial,
        )
        callbacks = []
        if self.tuner_early_stop_patience:
            early_stopping_callback = tf.keras.callbacks.EarlyStopping(
                monitor="val_ndcg_stateless",
                patience=self.tuner_early_stop_patience,
                mode="max",
            )
            callbacks.append(early_stopping_callback)
        tuner.search(
            train_ds,
            validation_data=dev_ds,
            epochs=self.tuner_epochs,
            callbacks=callbacks,
        )
        return tuner.get_best_hyperparameters()[0]

    def fit_linear_model(
        self, train_data, dev_data, feature_names, hyperparameters=None
    ):

        number_features = len(feature_names)

        train_ds = self.create_dataset(
            df_or_file=train_data, feature_names=feature_names
        )
        dev_ds = self.create_dataset(df_or_file=dev_data, feature_names=feature_names)
        with self.distribute_strategy.scope():
            linear_hyper_model = LinearHyperModel(
                number_documents_per_query=self.number_documents_per_query,
                number_features=number_features,
                top_n=self.top_n,
                learning_rate_range=self.learning_rate_range,
            )
        if not hyperparameters:
            best_hps = self.tune_model(
                model=linear_hyper_model, train_ds=train_ds, dev_ds=dev_ds
            )
            best_hyperparams = best_hps.values
        else:
            best_hyperparams = hyperparameters
            best_hps = kt.HyperParameters()
            best_hps.values = hyperparameters
        model = linear_hyper_model.build(best_hps)
        model.fit(
            train_ds,
            validation_data=dev_ds,
            epochs=self.final_epochs,
        )
        weights = model.get_weights()
        weights = {
            "feature_names": feature_names,
            "linear_model_weights": [
                float(weights[0][idx][0]) for idx in range(len(feature_names))
            ],
        }
        eval_result_from_fit = model.history.history["val_ndcg_stateless"][-1]

        return weights, eval_result_from_fit, best_hyperparams

    def fit_lasso_linear_model(
        self, train_data, dev_data, feature_names, hyperparameters=None
    ):

        number_features = len(feature_names)
        train_ds = self.create_dataset(
            df_or_file=train_data, feature_names=feature_names
        )
        dev_ds = self.create_dataset(df_or_file=dev_data, feature_names=feature_names)
        with self.distribute_strategy.scope():
            trained_normalization_layer = self.create_and_train_normalization_layer(
                train_ds=train_ds
            )
            lasso_hyper_model = LassoHyperModel(
                number_documents_per_query=self.number_documents_per_query,
                number_features=number_features,
                trained_normalization_layer=trained_normalization_layer,
                top_n=self.top_n,
                l1_penalty_range=self.l1_penalty_range,
                learning_rate_range=self.learning_rate_range,
            )
        if not hyperparameters:
            best_hps = self.tune_model(
                model=lasso_hyper_model, train_ds=train_ds, dev_ds=dev_ds
            )
            best_hyperparams = best_hps.values
        else:
            best_hyperparams = hyperparameters
            best_hps = kt.HyperParameters()
            best_hps.values = hyperparameters
        model = lasso_hyper_model.build(best_hps)
        model.fit(
            train_ds,
            validation_data=dev_ds,
            epochs=self.final_epochs,
        )
        weights = model.get_weights()
        weights = {
            "feature_names": feature_names,
            "normalization_mean": weights[0].tolist(),
            "normalization_sd": weights[1].tolist(),
            "normalization_number_data": int(weights[2]),
            "linear_model_weights": [
                float(weights[3][idx][0]) for idx in range(len(feature_names))
            ],
        }
        eval_result_from_fit = model.history.history["val_ndcg_stateless"][-1]

        return weights, eval_result_from_fit, best_hyperparams

    def lasso_model_search(
        self,
        train_data,
        dev_data,
        feature_names,
        protected_features=None,
        hyperparameter=None,
        output_file="lasso_model_search.json",
    ):

        output_file = os.path.join(self.folder_dir, output_file)
        try:
            with open(output_file, "r") as f:
                results = json.load(f)
                print("Lasso model search: Results from output file loaded.")
        except FileNotFoundError:
            print("Lasso model search: File not found. Starting search from scratch.")
            results = []

        if not protected_features:
            protected_features = []
        while (len(feature_names) >= len(protected_features)) and len(
            feature_names
        ) > 0:
            (weights, evaluation, best_hyperparams) = self.fit_lasso_linear_model(
                train_data=train_data,
                dev_data=dev_data,
                feature_names=feature_names,
                hyperparameters=hyperparameter,
            )
            partial_result = {
                "evaluation": evaluation,
                "weights": weights,
                "best_hyperparams": best_hyperparams,
            }
            results.append(partial_result)
            with open(output_file, "w") as f:
                json.dump(results, f)

            weights = {
                feature_name: float(model_weight)
                for feature_name, model_weight in zip(
                    weights["feature_names"], weights["linear_model_weights"]
                )
            }
            print({k: round(weights[k], 2) for k in weights})
            print(evaluation)

            abs_weights = {k: abs(weights[k]) for k in weights}
            if protected_features:
                abs_weights = {
                    k: abs_weights[k]
                    for k in abs_weights
                    if k not in protected_features
                }
            if len(abs_weights) > 0:
                worst_feature = min(abs_weights, key=abs_weights.get)
                feature_names = [x for x in feature_names if x != worst_feature]
            else:
                break

        return results

    def _forward_selection_iteration(
        self, train_data, dev_data, feature_names, hyperparameter=None
    ):
        (weights, evaluation, best_hyperparams) = self.fit_lasso_linear_model(
            train_data=train_data,
            dev_data=dev_data,
            feature_names=feature_names,
            hyperparameters=hyperparameter,
        )
        partial_result = {
            "number_features": len(feature_names),
            "evaluation": evaluation,
            "weights": weights,
            "best_hyperparams": best_hyperparams,
        }
        weights = {
            feature_name: float(model_weight)
            for feature_name, model_weight in zip(
                weights["feature_names"], weights["linear_model_weights"]
            )
        }
        print({k: round(weights[k], 2) for k in weights})
        print(evaluation)
        return partial_result

    def forward_selection_model_search(
        self,
        train_data,
        dev_data,
        feature_names,
        maximum_number_of_features=None,
        output_file="forward_selection_model_search.json",
        protected_features=None,
        hyperparameter=None,
    ):

        output_file = os.path.join(self.folder_dir, output_file)
        try:
            with open(output_file, "r") as f:
                results = json.load(f)
                print(
                    "Forward selection model search: Results from output file loaded."
                )
        except FileNotFoundError:
            print(
                "Forward selection model search: File not found. Starting search from scratch."
            )
            results = []

        if not maximum_number_of_features:
            maximum_number_of_features = len(feature_names)
        maximum_number_of_features = min(maximum_number_of_features, len(feature_names))

        if not protected_features:
            protected_features = []
        else:
            partial_result = self._forward_selection_iteration(
                train_data=train_data,
                dev_data=dev_data,
                feature_names=protected_features,
                hyperparameter=hyperparameter,
            )
            results.append(partial_result)
        while len(protected_features) < maximum_number_of_features:
            best_eval = 0
            best_features = None
            feature_names = [x for x in feature_names if x not in protected_features]
            for new_feature in feature_names:
                experimental_features = protected_features + [new_feature]
                partial_result = self._forward_selection_iteration(
                    train_data=train_data,
                    dev_data=dev_data,
                    feature_names=experimental_features,
                    hyperparameter=hyperparameter,
                )
                evaluation = partial_result["evaluation"]
                results.append(partial_result)
                if evaluation > best_eval:
                    best_eval = evaluation
                    best_features = experimental_features
                with open(output_file, "w") as f:
                    json.dump(results, f)
            protected_features = best_features
        return results

