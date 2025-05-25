import plotly.figure_factory as ff

with tabs[8]:
    st.subheader("Advanced Analytics")

    # --- 1. Correlation Matrix (Heatmap) ---
    st.markdown("**Correlation Matrix (Heatmap)**")
    numeric_cols = ["predicted_credit_score", "phl_risk_score", "latitude", "longitude"]
    corr = filtered_df[numeric_cols].corr()
    fig_corr = ff.create_annotated_heatmap(
        z=corr.values,
        x=list(corr.columns),
        y=list(corr.columns),
        annotation_text=np.round(corr.values, 2),
        colorscale='Viridis')
    st.plotly_chart(fig_corr, use_container_width=True)
    insight_card(
        "Correlation Matrix",
        "This chart uncovers which variables are strongly related. For example, a high correlation between PHL risk and latitude may reveal geography-driven losses. Strong correlations can inform predictive modeling or targeted interventions."
    )

    # --- 2. Parallel Categories (Intervention Adoption by Credit, Region, Risk) ---
    st.markdown("**Parallel Categories: Interventions, Regions, Credit, PHL Risk**")
    fig_parallel = px.parallel_categories(
        filtered_df,
        dimensions=["region", "interventions_adopted", "predicted_credit_score", "phl_risk_score"],
        color="predicted_credit_score",
        color_continuous_scale=px.colors.sequential.Inferno
    )
    st.plotly_chart(fig_parallel, use_container_width=True)
    insight_card(
        "Parallel Categories Analysis",
        "See how regions, interventions, and farmer scores interconnect. For example, you may discover some regions adopt certain interventions more often and tend to have lower PHL risk or higher credit scores."
    )

    # --- 3. Box Plot: PHL Risk by Intervention ---
    st.markdown("**Box Plot: PHL Risk by Intervention**")
    fig_box = px.box(
        filtered_df,
        x="interventions_adopted",
        y="phl_risk_score",
        color="interventions_adopted",
        points="all"
    )
    st.plotly_chart(fig_box, use_container_width=True)
    insight_card(
        "PHL Risk by Intervention",
        "This box plot compares the distribution of post-harvest loss risk across different interventions. Interventions with lower median risk and less variability are likely most effective."
    )

    # --- 4. Credit Score vs PHL Risk (Scatter with Trendline) ---
    st.markdown("**Scatter: Credit Score vs PHL Risk (with Trendline)**")
    fig_scatter = px.scatter(
        filtered_df,
        x="predicted_credit_score",
        y="phl_risk_score",
        color="region",
        trendline="ols",
        hover_data=["interventions_adopted"]
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    insight_card(
        "Credit Score vs. PHL Risk",
        "Investigate how creditworthiness relates to post-harvest loss risk. Outliers may indicate farmers with strong credit but high risk (or vice versa), suggesting areas for targeted support."
    )

    # --- 5. Sunburst: Region → Intervention → PHL Risk Quantile ---
    st.markdown("**Sunburst: Region → Intervention → PHL Risk Quantile**")
    filtered_df["phl_risk_quantile"] = pd.qcut(filtered_df["phl_risk_score"], 3, labels=["Low", "Medium", "High"])
    filtered_df["phl_risk_quantile"] = filtered_df["phl_risk_quantile"].astype(str)  # Fix for Categorical error
    fig_sunburst = px.sunburst(
        filtered_df,
        path=["region", "interventions_adopted", "phl_risk_quantile"],
        values="predicted_credit_score",
        color="phl_risk_quantile",
        color_discrete_map={"Low":"#66bb6a", "Medium":"#ffa726", "High":"#ef5350"}
    )
    st.plotly_chart(fig_sunburst, use_container_width=True)
    insight_card(
        "Sunburst: Region → Intervention → PHL Risk",
        "This nested chart shows how interventions are distributed across regions and how they impact PHL risk. Use it to spot which interventions drive risk down in specific regions."
    )

    # --- 6. Violin Plot: Credit Score Distribution by Region ---
    st.markdown("**Violin Plot: Credit Score by Region**")
    fig_violin = px.violin(
        filtered_df,
        y="predicted_credit_score",
        x="region",
        box=True,
        points="all",
        color="region"
    )
    st.plotly_chart(fig_violin, use_container_width=True)
    insight_card(
        "Credit Score Distribution by Region",
        "Violin plots reveal the full distribution of credit scores within each region, highlighting disparities and regions with more uniform or extreme credit profiles."
    )