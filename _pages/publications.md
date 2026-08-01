---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

{% include base_path %}

## Under Review / Preprints

{% assign preprints = site.publications | where: "category", "under-review" | sort: "date" | reverse %}
{% for post in preprints %}
  {% include archive-single.html %}
{% endfor %}

## Publications

{% assign papers = site.publications | where: "category", "published" | sort: "date" | reverse %}
{% for post in papers %}
  {% include archive-single.html %}
{% endfor %}
