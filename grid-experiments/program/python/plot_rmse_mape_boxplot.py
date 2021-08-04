# -*- coding: utf-8 -*-
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

filename_base_result = 'D:\\document\\matching probability\\data\\version2\\result\\'
column_names = ['whole_matching_probability', 'shared_distance', 'traveling_distance']
column_names_alternative = ['pw', 'ew', 'lw']
column_names_alternative_for_print = [r'$p_w$', r'$e_w$', r'$l_w$']
prefixes = ['rmse_', 'mape_']
prefixes_alternative = ['rmse', 'mape']

def get_rmse_mape_data():
    filename = filename_base_result + 'rmse_mape.csv'
    df = pd.read_csv(filename, sep = ',')
    return df

def to_percent(temp, position):
    return '%1.2f'%(100*temp) + '%'

def to_percent1(temp, position):
    return '%1.2f'%(temp) + '%'

def plot_rmse_mape_boxplot_separately1(df):
    fig = plt.figure(figsize = (20, 8))
    #xlabels = ['OD CATEGORY', 'OD CATEGORY', 'OD CATEGORY', 'OD CATEGORY', 'OD CATEGORY', 'OD CATEGORY']
    ylabels = [r'RMSE of $p_w$', r'RMSE of $e_w$ and $l_w$ (grid)', r'MAPE of $p_w$, $e_w$ and $l_w$']
    font2 = {'family' : 'Times New Roman',
             'weight' : 'normal',
             'size'   : 22
             }
    
    plt.subplot(131)
    ax1 = sns.boxplot(data = df['rmse_whole_matching_probability'].tolist())
    
    plt.subplot(132)
    df2 = pd.DataFrame(columns = ['data', 'name'])
    for i in range(len(df)):
        df2.loc[2 * i, 'data'] = df.loc[i, 'rmse_shared_distance']
        df2.loc[2 * i, 'name'] = r'$e_w$'
        df2.loc[2 * i + 1, 'data'] = df.loc[i, 'rmse_traveling_distance']
        df2.loc[2 * i + 1, 'name'] = r'$l_w$'
    ax2 = sns.boxplot(x = df2['name'].tolist(), y = df2['data'].tolist())
    
    plt.subplot(133)
    df3 = pd.DataFrame(columns = ['data', 'name'])
    for i in range(len(df)):
        df3.loc[3 * i, 'data'] = df.loc[i, 'mape_whole_matching_probability']
        df3.loc[3 * i, 'name'] = r'$p_w$'
        df3.loc[3 * i + 1, 'data'] = df.loc[i, 'mape_shared_distance']
        df3.loc[3 * i + 1, 'name'] = r'$e_w$'
        df3.loc[3 * i + 2, 'data'] = df.loc[i, 'mape_traveling_distance']
        df3.loc[3 * i + 2, 'name'] = r'$l_w$'
    ax3 = sns.boxplot(x = df3['name'].tolist(), y = df3['data'].tolist())
    
    axes = [ax1, ax2, ax3]
    for temp in range(len(axes)):
        ax = axes[temp]
        ax.spines['bottom'].set_linewidth(2);###设置底部坐标轴的粗细
        ax.spines['left'].set_linewidth(2);####设置左边坐标轴的粗细
        ax.spines['right'].set_linewidth(2);###设置右边坐标轴的粗细
        ax.spines['top'].set_linewidth(2);####设置上部坐标轴的粗细
        #ax.set_xlabel(xlabels[temp], font2)
        ax.set_ylabel(ylabels[temp], font2)
    ax1.yaxis.set_major_formatter(FuncFormatter(to_percent))
    ax2.yaxis.set_major_formatter(FuncFormatter(to_percent1))
    ax3.yaxis.set_major_formatter(FuncFormatter(to_percent1))
    
def plot_rmse_mape_boxplot_separately(df):
    fig = plt.figure(figsize = (20, 16))
    #xlabels = ['OD CATEGORY', 'OD CATEGORY', 'OD CATEGORY', 'OD CATEGORY', 'OD CATEGORY', 'OD CATEGORY']
    ylabels = [r'RMSE of $p_w$', r'RMSE of $e_w$ (grid)', r'RMSE of $l_w$ (grid)', r'MAPE of $p_w$', r'MAPE of $e_w$', r'MAPE of $l_w$']
    font2 = {'family' : 'Times New Roman',
             'weight' : 'normal',
             'size'   : 22
             }
    plt.subplots_adjust(wspace = 0.5, hspace = 0.2)
    axes = []
    for i in range(len(prefixes)):
        for j in range(len(column_names)):
            temp = 3*i + j
            plt.subplot(230 + temp + 1)
            column_name = column_names[j]
            prefix = prefixes[i]
            df['rate'] = column_names_alternative_for_print[j]
            x_data = df.rate.tolist()
            y_data = df[prefix + column_name].tolist()
            ax = sns.boxplot(x = x_data, y = y_data)
            axes.append(ax)
            
            ax.spines['bottom'].set_linewidth(2);###设置底部坐标轴的粗细
            ax.spines['left'].set_linewidth(2);####设置左边坐标轴的粗细
            ax.spines['right'].set_linewidth(2);###设置右边坐标轴的粗细
            ax.spines['top'].set_linewidth(2);####设置上部坐标轴的粗细
            #plt.xlabel(xlabels[temp], font2)
            plt.ylabel(ylabels[temp], font2)
            plt.tick_params(labelsize = 24)
    axes[0].yaxis.set_major_formatter(FuncFormatter(to_percent))
    axes[3].yaxis.set_major_formatter(FuncFormatter(to_percent1))
    axes[4].yaxis.set_major_formatter(FuncFormatter(to_percent1))
    axes[5].yaxis.set_major_formatter(FuncFormatter(to_percent1))
    
    axes[0].set_ylim(0, 0.04)
    filename_fig = filename_base_result + 'pictures\\error_boxplot.tif'
    plt.savefig(filename_fig) 

if __name__ == "__main__":
    df = get_rmse_mape_data()
    #plot_rmse_mape_boxplot_separately1(df)
    plot_rmse_mape_boxplot_separately(df)