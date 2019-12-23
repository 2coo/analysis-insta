import pandas as pd
import featuretools as ft
import numpy as np

def load_instagram_data(data_dir="", remove_gap=False, duration=True):
    df_ad_account = pd.read_csv(f"{data_dir}/ad_account.csv")    
    df_campaign = pd.read_csv(f"{data_dir}/campaign.csv")
    df_ad_set = pd.read_csv(f"{data_dir}/ad_set.csv")
    df_ad = pd.read_csv(f"{data_dir}/ad.csv")
    df_insight = pd.read_csv(f"{data_dir}/insight.csv")
    df_insight["id"] = df_insight.index
    df_creative = pd.read_csv(f"{data_dir}/creative.csv")

    df_video = pd.read_csv(f"{data_dir}/video_s3.csv").rename(columns={
        "video_id": "id"
    }).merge(pd.read_csv(f"{data_dir}/video.csv"), on="id", how="inner")

    df_image = pd.read_csv(f"{data_dir}/image_s3.csv")
    df_image["id"] = df_image.index

    es = ft.EntitySet(id='entityset')

    es = es.entity_from_dataframe(entity_id="ad_account",
                                dataframe=df_ad_account,
                                index="id"
                            )
    es = es.entity_from_dataframe(entity_id="campaign",
                                dataframe=df_campaign,
                                index="id",
                                    variable_types={
                                        "account_id": ft.variable_types.Id,
                                        "source_campaign_id": ft.variable_types.Id,
                                        "boosted_object_id": ft.variable_types.Id
                                    }
                                )
    es = es.entity_from_dataframe(entity_id="ad_set",
                                dataframe=df_ad_set,
                                index="id",
                                    variable_types={
                                        "account_id": ft.variable_types.Id,
                                        "campaign_id": ft.variable_types.Id,
                                        "source_adset_id": ft.variable_types.Id,
                                        "promoted_object_pixel_id": ft.variable_types.Id,
                                        "targeting_excluded_connections_id": ft.variable_types.Id,
                                        "rf_prediction_id": ft.variable_types.Id, 
                                        "instagram_actor_id": ft.variable_types.Id,
                                    }
                                )

    es = es.entity_from_dataframe(entity_id="ad",
                            dataframe=df_ad,
                            index="id",
                                variable_types={
                                    "account_id": ft.variable_types.Id,
                                    "campaign_id": ft.variable_types.Id,
                                    "adset_id": ft.variable_types.Id,
                                    "source_ad_id": ft.variable_types.Id,
                                },
                            )

    es = es.entity_from_dataframe(entity_id="insight",
                            dataframe=df_insight,
                            index="id"
                            )
                            
    es = es.entity_from_dataframe(entity_id="creative",
                            dataframe=df_creative,
                            index="id",
                                variable_types={
                                    "account_id": ft.variable_types.Id,
                                    "ad_id": ft.variable_types.Id,
                                    "actor_id": ft.variable_types.Id,
                                },
                            )
    es = es.entity_from_dataframe(entity_id="video",
                            dataframe=df_video,
                            index="id"
                            )
    es = es.entity_from_dataframe(entity_id="image",
                            dataframe=df_image,
                            index="id"
                            )
    
    es = es.add_relationship(ft.Relationship(es["ad_account"]["id"], es["campaign"]["account_id"]))
    es = es.add_relationship(ft.Relationship(es["campaign"]["id"], es["ad_set"]["campaign_id"]))
    es = es.add_relationship(ft.Relationship(es["ad_set"]["id"], es["ad"]["adset_id"]))
    es = es.add_relationship(ft.Relationship(es["ad"]["id"], es["insight"]["ad_id"]))
    es = es.add_relationship(ft.Relationship(es["ad"]["id"], es["creative"]["ad_id"]))
    es = es.add_relationship(ft.Relationship(es["creative"]["id"], es["video"]["creative_id"]))
    es = es.add_relationship(ft.Relationship(es["creative"]["id"], es["image"]["creative_id"]))
    return es

