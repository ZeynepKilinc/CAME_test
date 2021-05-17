# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 20:11:08 2021

@author: Xingyan Liu
"""

import os
from pathlib import Path
from typing import Sequence, Union, Mapping, List, Optional  # , Callable
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

import scanpy as sc
from scipy import sparse
from scipy.special import softmax

import networkx as nx
import torch
import logging

from . import (
    save_pickle,
    make_nowtime_tag,
    write_info,
    as_probabilities,
    predict_from_logits,
    subsample_each_group,
)
from .PARAMETERS import (
    get_model_params,
    get_loss_params,
    get_preprocess_params
)
from . import pp as utp
from . import pl as uplt
# from CAME_v0.utils import plot as uplt
from .utils import base, evaluation
# from CAME_v0.utils.train import prepare4train, Trainer
from . import (
    CGGCNet, datapair_from_adatas,
    CGCNet, aligned_datapair_from_adatas
)
from .utils._train_with_ground_truth import prepare4train, Trainer, seed_everything

PARAMS_MODEL = get_model_params()
PARAMS_PRE = get_preprocess_params()
PARAMS_LOSS = get_loss_params()

# In[]
'''============================[ MAIN FUNCTION ]==========================='''


def main_for_aligned(
        adatas: sc.AnnData,
        vars_feat: Sequence,
        vars_as_nodes: Optional[Sequence] = None,
        scnets: Optional[Sequence[sparse.spmatrix]] = None,
        dataset_names: Sequence[str] = ('reference', 'query'),
        key_class1: str = 'cell_ontology_class',
        key_class2: Optional[str] = None,
        do_normalize: bool = False,
        n_epochs: int = 350,
        resdir: Union[Path, str] = None,
        tag_data: Optional[str] = None,  # for autometically deciding `resdir` for results saving
        params_pre: dict = PARAMS_PRE,
        params_model: dict = PARAMS_MODEL,
        params_lossfunc: dict = PARAMS_LOSS,
        check_umap: bool = False,  # TODO
        n_pass: int = 100,
):
    if resdir is None:
        tag_time = base.make_nowtime_tag()
        tag_data = dataset_names if tag_data is None else tag_data
        resdir = Path(f'{tag_data}-{tag_time}')
    else:
        resdir = Path(resdir)

    figdir = resdir / 'figs'
    utp.check_dirs(figdir)
    sc.settings.figdir = figdir
    utp.check_dirs(resdir)
    # keys for training process
    if key_class2 is None:
        if key_class1 in adatas[1].obs.columns:
            key_class2 = key_class1
            keys = [key_class1, key_class2]
        else:
            key_class2 = 'clust_lbs'
            keys = [key_class1, None]
    else:
        keys = [key_class1, key_class2]
    keys_compare = [key_class1, key_class2]

    if do_normalize:
        adatas = list(map(lambda a: utp.normalize_default(a, force_return=True), adatas))

    logging.info('Step 1: preparing DataPair object...')
    adpair = aligned_datapair_from_adatas(
        adatas,
        vars_feat=vars_feat,
        vars_as_nodes=vars_as_nodes,
        oo_adjs=scnets,
        dataset_names=dataset_names,
    )

    ENV_VARs = prepare4train(adpair, key_class=keys, )

    logging.debug(ENV_VARs.keys())
    G = ENV_VARs['G']
    classes0 = ENV_VARs['classes']
    classes = classes0[:-1] if 'unknown' in classes0 else classes0
    n_classes = len(classes)

    params_model.update(
        in_dim_dict={'cell': adpair.n_feats, 'gene': 0},
        out_dim=n_classes,
        layernorm_ntypes=G.ntypes,
    )

    # model = None
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = CGCNet(G, **params_model)

    ''' Training '''
    trainer = Trainer(model=model, g=G, dir_main=resdir, **ENV_VARs)
    trainer.train(n_epochs=n_epochs,
                  params_lossfunc=params_lossfunc,
                  n_pass=n_pass, )
    trainer.save_model_weights()
    trainer.load_model_weights()  # 127)
    # trainer.load_model_weights(trainer._cur_epoch)
    test_acc = trainer.test_acc[trainer._cur_epoch_adopted]

    # ========================== record results ========================
    trainer.write_train_logs()

    write_info(resdir / 'info.txt',
               current_performance=trainer._cur_log,
               params_model=params_model,
               graph=G,
               model=model,
               )
    trainer.plot_cluster_index(fp=figdir / 'cluster_index.png')

    # ======================== Gather results ======================
    obs_ids1, obs_ids2 = adpair.get_obs_ids(0, False), adpair.get_obs_ids(1, False)
    out_cell = trainer.eval_current()['cell']

    labels_cat = adpair.get_obs_labels(keys, asint=False)
    probas_all = as_probabilities(out_cell)
    cl_preds = predict_from_logits(probas_all, classes=classes)
    obs = pd.DataFrame(
        {key_class1: labels_cat,  # true labels with `unknown` for unseen classes in query data
         'celltype': adpair.get_obs_anno(keys_compare),  # labels for comparison
         'predicted': cl_preds,
         'max_probs': np.max(probas_all, axis=1),
         })
    obs['is_right'] = obs['predicted'] == obs[key_class1]
    df_probs = pd.DataFrame(probas_all, columns=classes)
    adpair.set_common_obs_annos(obs)
    adpair.set_common_obs_annos(df_probs, ignore_index=True)
    adpair.obs.to_csv(resdir / 'obs.csv')
    save_pickle(adpair, resdir / 'adpair.pickle')
    # adding labels, predicted probabilities
    #    adata1.obs[key_class1] = pd.Categorical(obs[key_class1][obs_ids1], categories=classes)
    #    adata2.obs['predicted'] = pd.Categorical(obs['predicted'][obs_ids2], categories=classes)
    #    utp.add_obs_annos(adata2, df_probs.iloc[obs_ids2], ignore_index=True)

    # hidden states are stored in sc.AnnData to facilitated downstream analysis
    h_dict = model.get_hidden_states()  # trainer.feat_dict, trainer.g)
    adt = utp.make_adata(h_dict['cell'], obs=adpair.obs, assparse=False)
    #    gadt = utp.make_adata(h_dict['gene'], obs = adpair.var, assparse=False)

    ### group counts statistics (optinal)
    gcnt = utp.group_value_counts(adpair.obs, 'celltype', group_by='dataset')
    logging.debug(str(gcnt))
    gcnt.to_csv(resdir / 'group_counts.csv')

    # ============= confusion matrix & alluvial plot ==============
    sc.set_figure_params(fontsize=10)

    lblist_y = [labels_cat[obs_ids1], labels_cat[obs_ids2]]
    lblist_x = [cl_preds[obs_ids1], cl_preds[obs_ids2]]

    uplt.plot_confus_multi_mats(
        lblist_y,
        lblist_x,
        classes_on=classes,
        fname=figdir / f'confusion_matrix(acc{test_acc:.1%}).png',
    )
    # ============== heatmap of predicted probabilities ==============
    name_label = 'celltype'
    cols_anno = ['celltype', 'predicted'][:]

    # df_lbs = obs[cols_anno][obs[key_class1] == 'unknown'].sort_values(cols_anno)
    df_lbs = obs[cols_anno].iloc[obs_ids2].sort_values(cols_anno)

    indices = subsample_each_group(df_lbs['celltype'], n_out=50, )
    # indices = df_lbs.index
    df_data = df_probs.loc[indices, :].copy()
    df_data = df_data[sorted(df_lbs['predicted'].unique())]  # .T
    lbs = df_lbs[name_label][indices]

    _ = uplt.heatmap_probas(df_data.T, lbs, name_label='true label',
                            figsize=(5, 3.),
                            fp=figdir / f'heatmap_probas.pdf'
                            )
    return adpair, trainer, h_dict


def main_for_unaligned(
        adatas: sc.AnnData,
        vars_use: Sequence[Sequence],
        vars_as_nodes: Sequence[Sequence],
        df_varmap: pd.DataFrame,
        df_varmap_1v1: Optional[pd.DataFrame] = None,
        scnets: Optional[Sequence[sparse.spmatrix]] = None,
        dataset_names: Sequence[str] = ('reference', 'query'),
        key_class1: str = 'cell_ontology_class',
        key_class2: Optional[str] = None,
        do_normalize: bool = False,
        n_epochs: int = 350,
        resdir: Union[Path, str] = None,
        tag_data: Optional[str] = None,  # for autometically deciding `resdir` for results saving
        params_pre: dict = PARAMS_PRE,
        params_model: dict = PARAMS_MODEL,
        params_lossfunc: dict = PARAMS_LOSS,
        check_umap: bool = False,  # TODO
        n_pass: int = 100,
):
    if resdir is None:
        tag_time = base.make_nowtime_tag()
        tag_data = dataset_names if tag_data is None else tag_data
        resdir = Path(f'{tag_data}-{tag_time}')
    else:
        resdir = Path(resdir)

    figdir = resdir / 'figs'
    utp.check_dirs(figdir)
    sc.settings.figdir = figdir
    utp.check_dirs(resdir)
    # keys for training process
    if key_class2 is None:
        if key_class1 in adatas[1].obs.columns:
            key_class2 = key_class1
            keys = [key_class1, key_class2]
        else:
            key_class2 = 'clust_lbs'
            keys = [key_class1, None]
    else:
        keys = [key_class1, key_class2]
    keys_compare = [key_class1, key_class2]

    if do_normalize:
        adatas = list(map(
            lambda a: utp.normalize_default(a, force_return=True),
            adatas
        ))
    logging.info('preparing DataPair object...')
    dpair = datapair_from_adatas(
        adatas,
        vars_use=vars_use,
        df_varmap=df_varmap,
        df_varmap_1v1=df_varmap_1v1,
        oo_adjs=scnets,
        vars_as_nodes=vars_as_nodes,
        union_node_feats='auto',
        dataset_names=dataset_names,
    )

    ENV_VARs = prepare4train(dpair, key_class=keys, )

    logging.info(ENV_VARs.keys())
    G = ENV_VARs['G']
    classes0 = ENV_VARs['classes']
    classes = classes0[:-1] if 'unknown' in classes0 else classes0
    n_classes = len(classes)

    params_model.update(
        in_dim_dict={'cell': dpair.n_feats, 'gene': 0},
        out_dim=n_classes,
        layernorm_ntypes=G.ntypes,
    )

    # model = None
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = CGGCNet(G, **params_model)

    ''' Training '''
    trainer = Trainer(model=model, g=G, dir_main=resdir, **ENV_VARs)
    trainer.train(n_epochs=n_epochs,
                  params_lossfunc=params_lossfunc,
                  n_pass=n_pass, )
    trainer.save_model_weights()
    trainer.load_model_weights()  # 127)
    # trainer.load_model_weights(trainer._cur_epoch)
    test_acc = trainer.test_acc[trainer._cur_epoch_adopted]

    '''========================== record results ========================
    '''
    trainer.write_train_logs()

    write_info(resdir / 'info.txt',
               current_performance=trainer._cur_log,
               params_model=params_model,
               graph=G,
               model=model,
               )
    trainer.plot_cluster_index(fp=figdir / 'cluster_index.png')

    ''' ======================== Gather results ======================
    '''
    obs_ids1, obs_ids2 = dpair.get_obs_ids(0, False), dpair.get_obs_ids(1, False)
    out_cell = trainer.eval_current()['cell']

    labels_cat = dpair.get_obs_labels(keys, asint=False)
    probas_all = as_probabilities(out_cell)
    cl_preds = predict_from_logits(probas_all, classes=classes)
    obs = pd.DataFrame(
        {key_class1: labels_cat,  # true labels with `unknown` for unseen classes in query data
         'celltype': dpair.get_obs_anno(keys_compare),  # labels for comparison
         'predicted': cl_preds,
         'max_probs': np.max(probas_all, axis=1),
         })
    obs['is_right'] = obs['predicted'] == obs[key_class1]
    df_probs = pd.DataFrame(probas_all, columns=classes)
    dpair.set_common_obs_annos(obs)
    dpair.set_common_obs_annos(df_probs, ignore_index=True)
    dpair.obs.to_csv(resdir / 'obs.csv')
    save_pickle(dpair, resdir / 'dpair.pickle')
    # adding labels, predicted probabilities
    #    adata1.obs[key_class1] = pd.Categorical(obs[key_class1][obs_ids1], categories=classes)
    #    adata2.obs['predicted'] = pd.Categorical(obs['predicted'][obs_ids2], categories=classes)
    #    utp.add_obs_annos(adata2, df_probs.iloc[obs_ids2], ignore_index=True)

    # hidden states are stored in sc.AnnData to facilitated downstream analysis
    h_dict = model.get_hidden_states()  # trainer.feat_dict, trainer.g)
    adt = utp.make_adata(h_dict['cell'], obs=dpair.obs, assparse=False)
    #    gadt = utp.make_adata(h_dict['gene'], obs = adpair.var, assparse=False)

    ### group counts statistics (optinal)
    gcnt = utp.group_value_counts(dpair.obs, 'celltype', group_by='dataset')
    logging.info(str(gcnt))
    gcnt.to_csv(resdir / 'group_counts.csv')

    # ============= confusion matrix OR alluvial plot ==============
    sc.set_figure_params(fontsize=10)

    lblist_y = [labels_cat[obs_ids1], labels_cat[obs_ids2]]
    lblist_x = [cl_preds[obs_ids1], cl_preds[obs_ids2]]

    uplt.plot_confus_multi_mats(
        lblist_y,
        lblist_x,
        classes_on=classes,
        fname=figdir / f'confusion_matrix(acc{test_acc:.1%}).png',
    )
    # ============== heatmap of predicted probabilities ==============
    name_label = 'celltype'
    cols_anno = ['celltype', 'predicted'][:]

    # df_lbs = obs[cols_anno][obs[key_class1] == 'unknown'].sort_values(cols_anno)
    df_lbs = obs[cols_anno].iloc[obs_ids2].sort_values(cols_anno)

    indices = subsample_each_group(df_lbs['celltype'], n_out=50, )
    # indices = df_lbs.index
    df_data = df_probs.loc[indices, :].copy()
    df_data = df_data[sorted(df_lbs['predicted'].unique())]  # .T
    lbs = df_lbs[name_label][indices]

    _ = uplt.heatmap_probas(df_data.T, lbs, name_label='true label',
                            figsize=(5, 3.),
                            fp=figdir / f'heatmap_probas.pdf'
                            )
    return dpair, trainer, h_dict


def preprocess_aligned(
        adatas,
        key_class: str,
        df_varmap_1v1: Optional[pd.DataFrame] = None,
        use_scnets: bool = True,
        n_pcs: int = 30,
        nneigh_scnet: int = 5,
        nneigh_clust: int = 20,
        ntop_deg: int = 50,
):
    adatas = utp.align_adata_vars(
        adatas[0], adatas[1], df_varmap_1v1, unify_names=True,
    )

    logging.info('================ preprocessing ===============')
    params_preproc = dict(
        target_sum=None,
        n_top_genes=2000,
        n_pcs=n_pcs,
        nneigh=nneigh_scnet,
    )
    # NOTE: using the median total-counts as the scale factor (better than fixed number)
    adata1 = utp.quick_preprocess(adatas[0], **params_preproc)
    adata2 = utp.quick_preprocess(adatas[1], **params_preproc)

    # the single-cell network
    if use_scnets:
        scnets = [utp.get_scnet(adata1), utp.get_scnet(adata2)]
    else:
        scnets = None
    # get HVGs
    hvgs1, hvgs2 = utp.get_hvgs(adata1), utp.get_hvgs(adata2)

    # cluster labels
    key_clust = 'clust_lbs'
    clust_lbs2 = utp.get_leiden_labels(
        adata2, force_redo=True,
        nneigh=nneigh_clust,
        neighbors_key='clust',
        key_added=key_clust,
        copy=False
    )
    adatas[1].obs[key_clust] = clust_lbs2

    #    ntop_deg = 50
    params_deg = dict(n=ntop_deg, force_redo=False,
                      inplace=True, do_normalize=False)
    ### need to be normalized first
    degs1 = utp.compute_and_get_DEGs(
        adata1, key_class, **params_deg)
    degs2 = utp.compute_and_get_DEGs(
        adata2, key_clust, **params_deg)
    ###
    vars_feat = list(set(degs1).union(degs2))
    vars_node = list(set(hvgs1).union(hvgs2).union(vars_feat))

    dct = dict(
        adatas=adatas,
        vars_feat=vars_feat,
        vars_as_nodes=vars_node,
        scnets=scnets,
    )
    return dct, (adata1, adata2)


def preprocess_unaligned(
        adatas,
        key_class: str,
        use_scnets: bool = True,
        n_pcs: int = 30,
        nneigh_scnet: int = 5,
        nneigh_clust: int = 20,
        ntop_deg: int = 50,
):
    logging.info('================ preprocessing ===============')
    params_preproc = dict(
        target_sum=None,
        n_top_genes=2000,
        n_pcs=n_pcs,
        nneigh=nneigh_scnet,
    )
    # NOTE: using the median total-counts as the scale factor (better than fixed number)
    adata1 = utp.quick_preprocess(adatas[0], **params_preproc)
    adata2 = utp.quick_preprocess(adatas[1], **params_preproc)

    # the single-cell network
    if use_scnets:
        scnets = [utp.get_scnet(adata1), utp.get_scnet(adata2)]
    else:
        scnets = None
    # get HVGs
    hvgs1, hvgs2 = utp.get_hvgs(adata1), utp.get_hvgs(adata2)

    # cluster labels
    key_clust = 'clust_lbs'
    clust_lbs2 = utp.get_leiden_labels(
        adata2, force_redo=True,
        nneigh=nneigh_clust,
        neighbors_key='clust',
        key_added=key_clust,
        copy=False
    )
    adatas[1].obs[key_clust] = clust_lbs2

    params_deg = dict(n=ntop_deg, force_redo=False,
                      inplace=True, do_normalize=False)
    ### need to be normalized first
    degs1 = utp.compute_and_get_DEGs(
        adata1, key_class, **params_deg)
    degs2 = utp.compute_and_get_DEGs(
        adata2, key_clust, **params_deg)
    ###
    vars_use = [degs1, degs2]
    vars_as_nodes = [np.unique(np.hstack([hvgs1, degs1])),
                     np.unique(np.hstack([hvgs2, degs2]))]

    dct = dict(
        adatas=adatas,
        vars_use=vars_use,
        vars_as_nodes=vars_as_nodes,
        scnets=scnets,
    )
    return dct, (adata1, adata2)


def __test1__(n_epochs: int = 5):
    seed_everything()
    datadir = Path(os.path.abspath(__file__)).parent / 'sample_data'
    sp1, sp2 = ('human', 'mouse')
    dsnames = ('Baron_human', 'Baron_mouse')

    df_varmap_1v1 = pd.read_csv(datadir / f'gene_matches_1v1_{sp1}2{sp2}.csv', )

    dsn1, dsn2 = dsnames
    adata_raw1 = sc.read_h5ad(datadir / f'raw-{dsn1}.h5ad')
    adata_raw2 = sc.read_h5ad(datadir / f'raw-{dsn2}.h5ad')
    adatas = [adata_raw1, adata_raw2]

    key_class = 'cell_ontology_class'
    time_tag = make_nowtime_tag()
    resdir = Path('_temp') / f'{dsnames}-{time_tag}'

    came_inputs, (adata1, adata2) = preprocess_aligned(
        adatas,
        key_class=key_class,
        df_varmap_1v1=df_varmap_1v1,
    )

    adpair, trainer, _ = main_for_aligned(
        **came_inputs,
        dataset_names=dsnames,
        key_class1=key_class,
        key_class2=key_class,
        do_normalize=True,
        n_epochs=n_epochs,
        resdir=resdir,
        check_umap=not True,  # True for visualizing embeddings each 40 epochs
        n_pass=100,
    )

    del adpair, trainer, _
    torch.cuda.empty_cache()
    logging.debug('memory cleared\n')
    print('Test passed for ALIGNED!')


def __test2__(n_epochs: int = 5):
    seed_everything()
    datadir = Path(os.path.abspath(__file__)).parent / 'sample_data'
    sp1, sp2 = ('human', 'mouse')
    dsnames = ('Baron_human', 'Baron_mouse')

    df_varmap_1v1 = pd.read_csv(datadir / f'gene_matches_1v1_{sp1}2{sp2}.csv', )
    df_varmap = pd.read_csv(datadir / f'gene_matches_{sp1}2{sp2}.csv', )

    dsn1, dsn2 = dsnames
    adata_raw1 = sc.read_h5ad(datadir / f'raw-{dsn1}.h5ad')
    adata_raw2 = sc.read_h5ad(datadir / f'raw-{dsn2}.h5ad')
    adatas = [adata_raw1, adata_raw2]

    key_class = 'cell_ontology_class'
    time_tag = make_nowtime_tag()
    resdir = Path('_temp') / f'{dsnames}-{time_tag}'

    came_inputs, (adata1, adata2) = preprocess_unaligned(
        adatas,
        key_class=key_class,
    )

    dpair, trainer, _ = main_for_unaligned(
        **came_inputs,
        df_varmap=df_varmap,
        df_varmap_1v1=df_varmap_1v1,
        dataset_names=dsnames,
        key_class1=key_class,
        key_class2=key_class,
        do_normalize=True,
        n_epochs=n_epochs,
        resdir=resdir,
        check_umap=not True,  # True for visualizing embeddings each 40 epochs
        n_pass=100,
    )

    del dpair, trainer, _
    torch.cuda.empty_cache()
    logging.debug('memory cleared\n')
    print('Test passed for UN-ALIGNED!')