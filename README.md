# Hands on data analysis using Jupyter and Hadoop

# What is this talk about?

A tutorial of sorts.

Mostly a showcase of using Jupyter with the hadoop cluster.

Hopefully, you have something to play with after (or during this talk).


# Getting started
1. [**DS Lab**](https://lab.ds.trv.cloud/hub/home)

    *Pros*: no setup required, keytab file is the only requirement, interactive spark

    *Cons*: remote setup, need to ferry files, server sometimes goes down, harder to customize

2. [**MyJupyter Docker image**](https://github.com/trivago/myjupyter)

    *Pros*: super easy to setup, keytab file is the only requirement, interactive spark

    *Cons*: needs docker, not as easily customizable

3. **Custom environment (e.g. with** [**miniconda**](https://docs.conda.io/en/latest/miniconda.html)**)**

    *Pros*: highly customizable, sometime necessary if using esoteric libraries

    *Cons*: DIY option

![Special thanks to DAPA-Tools aka MPOPS aka Andrés’ Team.](https://paper-attachments.dropbox.com/s_A1BF12B3C78210718A24557EF851D90488A76523C0B1BBAECFC27AF048EAD789_1627393912679_image+1.png)



# What is Jupyter? Why use it?
> JupyterLab is a web-based interactive development environment for Jupyter notebooks, code, and data. JupyterLab is flexible: configure and arrange the user interface to support a wide range of workflows in data science, scientific computing, and machine learning.


- ***Python*** - Flexible and powerful general purpose programming language
-  ***Metadata*** - Markdown comments help remind someone else (usually the future you) of what you did and why. Can be committed to a repository.
- ***Compatibility with Dropbox paper*** - Dropbox paper also uses markdown, making it easy to transfer results from the Jupyter notebook to the Dropbox paper and visa versa.


- Basically, it gives you an interactive python environment that can interact with hadoop and can also contain markdown metadata
- Replaces Hue → Excel
- Matplotlib/Plotly/etc. makes prettier pictures.


# Quick and dirty tips
## Jupyter notebook keyboard shortcuts

**Edit mode shortcuts**

    - shift + enter: execute cell, move to next cell
    - ctrl + enter: execute cell in place

**Command mode**

- c - copy
- v - paste
- x - cut
- m - convert cell to markdown
- y - convert cell to code
- a - insert cell above
- b - insert cell below


# Example use cases
- Plotting revenue vs. ymd (see notebook)
- Basic exploratory data analysis (see notebook)
- Adding variables to queries (see notebook)
- Prototyping Oozie workflows (see [HSS-4734](https://tasks.trivago.com/browse/HSS-4734))
- C-test analysis


----------
# C-test template ([link to repository](https://github.com/trivago/ctest-template))
## Context

In every C-test, we do the following ‘due diligence’ analyses

- Release controller sanity checks - do you have the right rows?
- Topline KPI metrics
- Session - clickout metrics (`ssm.co_log_entries`)
    - Partner clickshare
    - Avg. clicked price / avg. clicked CPC
- Request based metrics
    - Ranking metrics - MRR, avg. impressed price, avg. impressed CPC
    - Metric breakouts
        - by hotel position
        - by hotel sort order
        - by search context

**Motivation**

- If you do something similar more than 2 times, think about automating it for the 3rd time onwards.
- Create code that is re-usable.

**Simple sanity check (C-test specific)**

    select
        -- indices
        if(array_contains(test_group_set_php.mantis_id, 57256L),
           'test', 'control') AS group_id,
        ssm.ymd as ymd,
        -- aggreates
        count(*) as visits,
        avg(ssm.pc_cos) as clickouts,
        avg(ssm.clickout_rev) as revenue
    from
        trivago_analytic.session_stats_master as ssm
    where
        ssm.crawler_id = 0
        and ssm.is_core
        and (array_contains(tags, 'releasecontrol'))
        -- ymd filter
        and ymd between 20210621 and 20210705
        -- traffic filter
        and (array_contains(control_group_set_php.mantis_id, 57256L)
             or array_contains(test_group_set_php.mantis_id, 57256L))
        and ssm.session_date_id between 2021062118*1e9 and 2021070523999999999
        and substr(cast(ssm.release_string as string), 1, 4) in ('9306', 'arp', '9307')
    group by    
        if(array_contains(test_group_set_php.mantis_id, 57256L),
           'test', 'control'),
        ssm.ymd
- Bold lines are specific to the C-test. It’s the same for all queries regarding the C-test.
- Non-bold lines say give me some aggregates (visits, clickouts, revenue) with some granularity (group_id, ymd)

**Simple sanity check (generic)**

    select
        -- indices
        {ssm_group_tags} AS group_id,
        ssm.ymd as ymd,
        -- aggreates
        count(*) as visits,
        avg(ssm.pc_cos) as clickouts,
        avg(ssm.clickout_rev) as revenue
    from
        trivago_analytic.session_stats_master as ssm
    where
        ssm.crawler_id = 0
        and ssm.is_core
        and (array_contains(tags, 'releasecontrol'))
        -- ymd filter
        and {ymd_filter}
        -- traffic filter
        and {ssm_traffic_filter}
    group by
        {ssm_group_tags},
        ssm.ymd

**Generating C-test tags**
Given

    query_kwargs = {'test_type': 'standard',
                    'test_id': 57256,
                    'ymd_start': 20210621,
                    'ymd_end': 20210705,
                    'ymdh_start': 2021062118,
                    'ymdh_end': 2021070523,
                    'release_strings': ('9306', 'arp', '9307')}

call tooling functions

    ssm_group_tags = u.get_group_tags(query_kwargs)
    ymd_filter, traffic_filter = u.get_test_filters(query_kwargs)

with outputs

`**ssm_group_tags**`:

    if(array_contains(test_group_set_php.mantis_id, 57256L),
       'test', 'control')

`**ymd_filter**`:

    ymd between 20210621 and 20210705

`**traffic_filter**`:

    (array_contains(control_group_set_php.mantis_id, 57256L)
     or array_contains(test_group_set_php.mantis_id, 57256L))
    and ssm.session_date_id between 2021062118*1e9 and 2021070523999999999
    and substr(cast(ssm.release_string as string), 1, 4) in ('9306', 'arp', '9307')
    and True

The variables is required in every query in the C-test analysis and does not normally change.
Abstracting them away allows you make queries that can be re-used on other C-tests.
