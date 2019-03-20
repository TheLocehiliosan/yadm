---
layout: splash
permalink: /
stars_button: '
{::nomarkdown}<iframe
src="https://ghbtns.com/github-btn.html?user=TheLocehiliosan&repo=yadm&type=star&count=true"
frameborder="0" scrolling="0" width="100"
height="20px" style="float: right;"></iframe>{:/nomarkdown}
'
title: Yet Another Dotfiles Manager
header:
  overlay_color: "#000"
  overlay_filter: 0.7
  overlay_image: /images/unsplash.jpg
  cta_label: Install Now
  cta_url: /docs/install
  caption: "_Photo: [Michael Jasmund](https://unsplash.com/photos/o51enAB_89A)_"
excerpt: '

When you live in a command line, configurations are a deeply personal thing.
They are often crafted over years of experience, battles lost, lessons learned,
advice followed, and ingenuity rewarded. When you are away from your own
configurations, you are an orphaned refugee in unfamiliar and hostile
surroundings. You feel clumsy and out of sorts. You are filled with a sense of
longing to be back in a place you know. A place you built. A place where all the
short-cuts have been worn bare by your own travels. A place you proudly call...
**$HOME**.

'
feature_row:
  - title: Overview
    alt: Overview
    btn_class: btn--inverse
    btn_label: Discover yadm
    image_path: /images/cogs-padding.png
    url: /docs/overview
    excerpt: '

        If you know how to use Git, you already know how to use **yadm**.
        **yadm** helps you maintain a single repository of dotfiles, while keeping
        them where they belong---in `$HOME`.
        Anything you can do with Git, you can do using **yadm**.

    '
  - title: Alternate Files
    alt: Alternates
    btn_class: btn--inverse
    btn_label: Details
    image_path: /images/copy-padding.png
    url: /docs/alternates
    excerpt: '

        Sometimes you need different configurations on different systems.
        **yadm** makes it possible to use alternate versions of files based on
        the OS or hostname of the system.

    '
  - title: Encryption
    alt: Encryption
    btn_class: btn--inverse
    btn_label: Learn more
    image_path: /images/secret-padding.png
    url: /docs/encryption
    excerpt: '

        Configurations occasionally include secrets such as passwords,
        encryption keys, or other sensitive information. **yadm** allows you to
        add such files to an encrypted archive, which can be maintained
        alongside your other configurations.

    '
  - title: Bootstrap
    alt: Bootstrap
    btn_class: btn--inverse
    btn_label: Explore how
    image_path: /images/tasks-padding.png
    url: /docs/bootstrap
    excerpt: '

        Define your own instructions to complete your dotfiles installation.
        If provided, **yadm** can execute your custom program immediately
        following a successful clone.

    '
  - title: FAQ
    alt: FAQ
    btn_class: btn--inverse
    btn_label: Get answers
    image_path: /images/question-circle-padding.png
    url: /docs/faq
    excerpt: '

        Have a question? You might find an answer in the FAQ.

    '
  - title: Manual
    alt: Manual
    btn_class: btn--inverse
    btn_label: See man page
    image_path: /images/book-padding.png
    url: https://github.com/TheLocehiliosan/yadm/blob/master/yadm.md
    excerpt: '

        View the manual online.

    '
  - title: Example Dotfiles
    alt: Examples
    btn_class: btn--inverse
    btn_label: View examples
    image_path: /images/keyboard-padding.png
    url: /docs/examples
    excerpt: '

        Need some inspiration? Here are some example dotfiles repository.

    '
---

{% include feature_row id="intro" type="center" %}

{% include feature_row %}
