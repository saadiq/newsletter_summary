---
layout: default
title: Newsletter Summary Archive
---

# Newsletter Summary Archive

Welcome to the automated newsletter summary archive. These summaries are generated using AI to distill key insights from various newsletter sources.

<div class="filter-section">
    <h3>Filter by Label</h3>
    <div id="label-filters">
        <button onclick="filterPosts('all')" class="filter-btn">All</button>
    </div>
</div>

<div id="post-list">
{% assign posts_by_date = site.posts | sort: 'date' | reverse %}
{% for post in posts_by_date %}
<div class="post-item" data-label="{{ post.label }}">
    <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
    <div class="post-meta">
        <span class="label-tag">{{ post.label }}</span>
        <time>{{ post.date | date: "%B %d, %Y" }}</time>
        {% if post.newsletter_count %}
        <span> • {{ post.newsletter_count }} newsletters analyzed</span>
        {% endif %}
    </div>
    {% if post.excerpt %}
    <p>{{ post.excerpt | strip_html | truncate: 200 }}</p>
    {% endif %}
    <a href="{{ post.url | relative_url }}">Read full summary →</a>
</div>
{% endfor %}
</div>

{% if site.posts.size == 0 %}
<p style="text-align: center; color: #666; margin: 3rem 0;">
    No summaries have been generated yet. Run the newsletter summarizer to create your first report!
</p>
{% endif %}

<script>
// Collect unique labels
const posts = document.querySelectorAll('.post-item');
const labels = new Set();
posts.forEach(post => {
    const label = post.dataset.label;
    if (label) labels.add(label);
});

// Add filter buttons for each label
const filterContainer = document.getElementById('label-filters');
labels.forEach(label => {
    const btn = document.createElement('button');
    btn.textContent = label.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    btn.onclick = () => filterPosts(label);
    btn.className = 'filter-btn';
    filterContainer.appendChild(btn);
});

// Filter function
function filterPosts(label) {
    const posts = document.querySelectorAll('.post-item');
    posts.forEach(post => {
        if (label === 'all' || post.dataset.label === label) {
            post.style.display = 'block';
        } else {
            post.style.display = 'none';
        }
    });
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.style.fontWeight = 'normal';
    });
    event.target.style.fontWeight = 'bold';
}
</script>

<style>
.filter-btn {
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
    padding: 0.3rem 0.8rem;
    border: 1px solid #007bff;
    background: white;
    color: #007bff;
    border-radius: 4px;
    cursor: pointer;
}
.filter-btn:hover {
    background: #007bff;
    color: white;
}
</style>