import os
import subprocess
import pandas as pd

from src.utils.types import StixQueryRegion

def query_stix(
    query_region: StixQueryRegion,
    output_dir: str,
    stix_bin: str,
    shardfile: str,
    parallel: bool = False,
    slop: int = 500,
):
    # parse shards
    df_shard = pd.read_csv(shardfile,sep="\t")
    df_shard.columns=['giggle_index', 'ped_db']
    num_shards = df_shard.shape[0]
    assert num_shards > 0

    # setup output
    stix_output_file = os.path.join(output_dir, query_region.file_name) + '.txt'

    # setup query
    l_query = (
        f"{query_region.chr}:{query_region.left_start}-{query_region.left_stop}"
    )
    r_query = f"{query_region.chr}:{query_region.right_start}-{query_region.right_stop}"

    # run queries
    for i,row in df_shard.iterrows():
        index_path=row['giggle_index']
        database_path=row['ped_db']
        if i == 0:
            operation='>'
        else:
            operation='>>'
        cmd = f"{stix_bin} -i {index_path} -d {database_path} "
        cmd += f"-s {slop} -t DEL -l {l_query} -r {r_query} -g "
        cmd += f"{operation} {stix_output_file}"
        print(f"# running cmd: {cmd}")
        result = subprocess.run(cmd,shell=True, capture_output=True,text=True)
    return stix_output_file
