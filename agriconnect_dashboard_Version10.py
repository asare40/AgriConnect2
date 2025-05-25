# ... (previous code remains unchanged)

# --- Analytics ---
with tabs[1]:
    st.subheader("📈 Enhanced Regional Analytics")
    st.markdown("Explore how credit scores and PHL risk differ by region with interactive charts and easy-to-read interpretations.")

    # Average Credit Score by Region - Horizontal Bar Chart
    st.markdown("**Average Credit Score by Region**")
    avg_credit_by_region = filtered_df.groupby("region")["predicted_credit_score"].mean().sort_values()
    fig_credit_bar = px.bar(
        x=avg_credit_by_region.values,
        y=avg_credit_by_region.index,
        orientation="h",
        color=avg_credit_by_region.values,
        color_continuous_scale="Blues",
        labels={"x": "Avg Credit Score", "y": "Region"},
        title="Average Credit Score by Region"
    )
    st.plotly_chart(fig_credit_bar, use_container_width=True)
    top_region = avg_credit_by_region.idxmax()
    st.success(f"**Interpretation:** The region with the highest average credit score is **{top_region}** ({avg_credit_by_region.max():.1f}).")

    # Average PHL Risk by Region - Horizontal Bar Chart
    st.markdown("**Average Post-Harvest Loss (PHL) Risk by Region**")
    avg_phl_by_region = filtered_df.groupby("region")["phl_risk_score"].mean().sort_values()
    fig_phl_bar = px.bar(
        x=avg_phl_by_region.values,
        y=avg_phl_by_region.index,
        orientation="h",
        color=avg_phl_by_region.values,
        color_continuous_scale="Reds",
        labels={"x": "Avg PHL Risk", "y": "Region"},
        title="Average PHL Risk by Region"
    )
    st.plotly_chart(fig_phl_bar, use_container_width=True)
    risk_region = avg_phl_by_region.idxmax()
    st.warning(f"**Interpretation:** The region with the highest PHL risk is **{risk_region}** ({avg_phl_by_region.max():.2f}). Consider prioritizing interventions here.")

    # Credit Score & PHL Risk Relationship - Scatter Plot
    st.markdown("**Credit Score vs. PHL Risk**")
    fig_scatter = px.scatter(
        filtered_df,
        x="predicted_credit_score",
        y="phl_risk_score",
        color="region",
        size="phl_risk_score",
        hover_data=["interventions_adopted"],
        trendline="ols",
        template="plotly_white",
        title="Relationship Between Credit Score and PHL Risk"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.info(
        "💡 **Interpretation:** This chart shows how farmer credit score relates to post-harvest loss risk across regions. "
        "Regions or farmers in the upper left (high PHL risk, low credit score) may benefit most from targeted support."
    )

    # Most Adopted Interventions - Pie Chart
    st.markdown("**Adoption of Interventions Among Farmers**")
    intervention_counts = filtered_df["interventions_adopted"].value_counts()
    fig_pie = px.pie(
        names=intervention_counts.index,
        values=intervention_counts.values,
        title="Distribution of Adopted Interventions"
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    most_adopted = intervention_counts.idxmax()
    st.success(f"**Interpretation:** The most widely adopted intervention is **{most_adopted}**.")

    insight_card(
        "Summary of Analytics",
        (
            "- Use the bar charts to quickly spot which regions excel and which need support.\n"
            "- The scatter plot helps you identify if credit access and PHL risk are linked for your farmers.\n"
            "- The intervention pie chart helps you see where your outreach is working best."
        ),
        color="#e1bee7"
    )

# ... (following code remains unchanged)