CREATE EXTERNAL TABLE database_name.table_name (
  event_date string,
  event_timestamp bigint,
  event_name string,
  event_params array<struct<
    key:string,
    value:struct<
      string_value:string,
      int_value:bigint,
      float_value:double,
      double_value:double
    >
  >>,
  event_previous_timestamp bigint,
  event_value_in_usd double,
  event_bundle_sequence_id bigint,
  event_server_timestamp_offset bigint,
  user_id string,
  user_pseudo_id string,
  privacy_info struct<analytics_storage:string, ads_storage:string, uses_transient_token:string>,
  user_properties array<struct<
    key:string,
    value:struct<string_value:string, int_value:bigint, float_value:double, double_value:double, set_timestamp_micros:bigint>>>,
  user_first_touch_timestamp bigint,
  user_ltv struct<revenue:double, currency:string>,
  device struct<
    category:string,
    mobile_brand_name:string,
    mobile_model_name:string,
    mobile_marketing_name:string,
    mobile_os_hardware_model:string,
    operating_system:string,
    operating_system_version:string,
    vendor_id:string,
    advertising_id:string,
    language:string,
    is_limited_ad_tracking:string,
    time_zone_offset_seconds:bigint,
    browser:string,
    browser_version:string,
    web_info:struct<
        browser:string,
        browser_version:string,
        hostname:string
        >
    >,
  geo struct<
	  city:string,
	  country:string,
	  continent:string,
	  region:string,
	  sub_continent:string,
	  metro:string
	>,
  app_info struct<id:string, version:string, install_store:string, firebase_app_id:string, install_source:string>,
  traffic_source struct<name:string, medium:string, source:string>,
  stream_id string,
  platform string,
  event_dimensions struct<hostname:string>,
  ecommerce struct<
    total_item_quantity:bigint,
    purchase_revenue_in_usd:double,
    purchase_revenue:double,
    refund_value_in_usd:double,
    refund_value:double,
    shipping_value_in_usd:double,
    shipping_value:double,
    tax_value_in_usd:double,
    tax_value:double,
    unique_items:bigint,
    transaction_id:string
>,
  items array<struct<
    item_id:string,
    item_name:string,
    item_brand:string,
    item_variant:string,
    item_category:string,
    item_category2:string,
    item_category3:string,
    item_category4:string,
    item_category5:string,
    price_in_usd:double,
    price:double,
    quantity:bigint,
    item_revenue_in_usd:double,
    item_revenue:double,
    item_refund_in_usd:double,
    item_refund:double,
    coupon:string,
    affiliation:string,
    location_id:string,
    item_list_id:string,
    item_list_name:string,
    item_list_index:string,
    promotion_id:string,
    promotion_name:string,
    creative_name:string,
    creative_slot:string,
    item_params:array<struct<
        key:string,
        value:struct<
            string_value:string,
            int_value:bigint,
            float_value:double,
            double_value:double
            >
        >
    >>>,
  collected_traffic_source struct<
    manual_campaign_id:string,
    manual_campaign_name:string,
    manual_source:string,
    manual_medium:string,
    manual_term:string,
    manual_content:string,
    manual_source_platform:string,
    manual_creative_format:string,
    manual_marketing_tactic:string,
    gclid:string,
    dclid:string,
    srsltid:string
    >,
  is_active_user boolean,
  batch_event_index bigint,
  batch_page_id bigint,
  batch_ordering_id bigint,
  session_traffic_source_last_click struct<
    manual_campaign:struct<
        campaign_id:string,
        campaign_name:string,
        source:string,
        medium:string,
        term:string,
        content:string,
        source_platform:string,
        creative_format:string,
        marketing_tactic:string
    >, google_ads_campaign:struct<
        customer_id:string,
        account_name:string,
        campaign_id:string,
        campaign_name:string,
        ad_group_id:string,
        ad_group_name:string
    >, cross_channel_campaign:struct<
        campaign_id:string,
        campaign_name:string,
        source:string,
        medium:string,
        source_platform:string,
        default_channel_group:string,
        primary_channel_group:string
    >, sa360_campaign:struct<
        campaign_id:string,
        campaign_name:string,
        source:string,
        medium:string,
        ad_group_id:string,
        ad_group_name:string,
        creative_format:string,
        engine_account_name:string,
        engine_account_type:string,
        manager_account_name:string
    >, cm360_campaign:struct<
        campaign_id:string,
        campaign_name:string,
        source:string,
        medium:string,
        account_id:string,
        account_name:string,
        advertiser_id:string,
        advertiser_name:string,
        creative_id:string,
        creative_format:string,
        creative_name:string,
        creative_type:string,
        creative_type_id:string,
        creative_version:string,
        placement_id:string,
        placement_cost_structure:string,
        placement_name:string,
        rendering_id:string,
        site_id:string,
        site_name:string
    >, dv360_campaign:struct<
        campaign_id:string,
        campaign_name:string,
        source:string,
        medium:string,
        advertiser_id:string,
        advertiser_name:string,
        creative_id:string,
        creative_format:string,
        creative_name:string,
        exchange_id:string,
        exchange_name:string,
        insertion_order_id:string,
        insertion_order_name:string,
        line_item_id:string,
        line_item_name:string,
        partner_id:string,
        partner_name:string
    >>,
  publisher struct<
    ad_revenue_in_usd:double,
    ad_format:string,
    ad_source_name:string,
    ad_unit_id:string
    >
)
PARTITIONED BY (
	event_date_part string
)
STORED AS PARQUET
LOCATION 's3://xxxxxxxx/xxxxxxxx';
