# human_cortical_single_neuron_models
Huamn cortical single cell simulation models for BMTK+neuron
- Bio-realistic: including representation of major ion channels
- All-active: Na and K channels on dendrites
- Ground with patch-seq experiments

Example:
simple_iclamp.py to simulate a single cell with square curent clamp

Enviroment requirement
- BMTK v1.1.1+
- neuron v8.+

firgures for analysis
Visualization of traces compare to experiments
![figure_traces](figure_traces/plot.png)
training progress for the genetic optimization
![figure_training_history](figure_training_history/ITL23__689309060_plot.png)
SOBOL sensitivity analysis 
![figure_sobol_analysis](figure_sobol_analysis/Excititory_summary_plot.png)
Model v RNA seq
![figure_sobol_analysis](figure_model_v_rna_seq/inh_scatter_w_lines_plots_HCN1_HCN2_HCN3_vs_gbar_Ih_somatic_gbar_Ih_basal.png)
Model v RNA seq
![figure_sobol_analysis](figure_UMAP_parameters/exc_umap_para.png)
![figure_sobol_analysis](figure_UMAP_parameters/inh_umap_para.png)
