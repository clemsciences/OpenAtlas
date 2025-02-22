FAQ
===

.. toctree::

Here you can find answers to some frequently asked questions.

How to manage multiple projects or case studies
-----------------------------------------------

Tag: technical

There are two main approaches on how to deal with multiple projects or case
studies:

Multiple instances
******************

If every project has their own instance (installation) of OpenAtlas then you
don't have to worry about separating the data later. But it would also mean
that data can't be used together, at least not directly.

Shared instance
***************

Projects (or case studies) can use the same instance which can be useful if
they share data, such as information about places or persons.

For data separation a custom :doc:`/entity/type` can be created,
usually called **Case study**, which can be:

* Attached to multiple classes (probably most of them)
* Set to **multiple** use so that a place can be part of multiple case
  studies
* Set to **required** so that users don't forget to choose at least one

Later on, e.g. when running analyses or developing a presentation site for one
case study, data can be filtered by case studies to separate the data sets
via the :doc:`/technical/api`.

How does data access work
-------------------------
Tag: design decision

If and when data saved in OpenAtlas is shared can be chosen at any point, but:

* All registered users have access to all model data
* Either **all** data is made public via the :doc:`/technical/api` or **none**
* Presentation sites can filter which data (e.g. which case study) is shown
  via the API
* Showing images is a special case because it also depends on licenses and the
  :doc:`/admin/iiif` server

There is no option (or plans to add one) to **hide** parts of the data for
specific users as that conflicts with one of our core value - to be open.
Furthermore, there are practical reasons, e.g. to avoid duplicates.
If a strict separation is needed, using multiple OpenAtlas instances might
be a better solution.

How to enter professions
------------------------
Tag: model

A profession is not entered via a type as a lot of other information you
will put into the database. You can enter a person’s profession by linking
them to a group.
This group consists of people with the same profession. Say you want to
enter our lead developer Alex into the database: create a group named
‘OpenAtlas’ and connect him to that group in the respective form. Here you
can pick the role he has in that group from a list of types. For a more
detailed tutorial on how to enter professions, have a look
:doc:`here</examples/profession>`.

.. _public_sharing_label:

How to make files available for the public
------------------------------------------
If you plan on sharing files with the public, e.g. on a presentation
site or a public archive, several criteria have to be met:

Criteria checked by the software
********************************
* The file must exist
* A license has to be specified
* The file has to be marked with **public sharing allowed**

In case these criteria aren't met, a file:

* Will not be shared via the :doc:`/technical/api`
* Will not show up on presentation sites developed by the OpenAtlas team
* Will not be included in long-term archiving via
  `ARCHE <https://arche.acdh.oeaw.ac.at/>`_

Be aware that although the file itself won't be shared, the file
information (such as filenames, etc.) will still be available (e.g. shown on a
presentation site).

At **file** -> **list** you find counts for:

* Public files
* Public files with a missing license
* Public files with a license but without creator (which many licenses require)

Criteria checked by users
*************************
* The linked license has to be the correct one and allow public sharing
* Other license specific criteria, e.g. specifying the creator, are met

There are many licenses with different criteria, e.g. a CC-BY 4.0 license
requires the attribution to the creator. Because it is not possible to check
these automatically, it is the responsibility of the project management to
ensure that all necessary requirements are met and to indicated it via setting
the **public sharing allowed** flag.

Be aware that licenses can be linked to an external reference (e.g. an URL)
which might be informative for other users or viewers.

Why can't a free text field be added via custom types
-----------------------------------------------------
Tag: design decision

A free text entry field would lead to lots of unstructured data.
Unstructured data can not be processed automatically and would result in it
neither being presented nor searchable in the OpenAtlas system as well as in a
presentation site. Therefore, we made the decision, not to include free text
types into the OpenAtlas system. Solutions to this problem are very case
specific, but you could:

* Use the provided description field to enter any type of free text
  (keep in mind that this also comes with restrictions on how to present the
  data on a presentation site)
* Create a new tree of project specific types for as many cases as possible
  and structure your data with them – for a step by step tutorial how to
  create new types, click :doc:`here</examples/types>`.

We are more than happy to help you find a solution tailored to your
project’s specific needs, so please don’t hesitate to reach out to us if you
have any additional questions on this topic.

Why can't longer texts be formatted
-----------------------------------
Tag: design decision

For formatting longer texts, e.g. entity descriptions, only linebreaks can
be used. The main reason for not implementing formatting systems like HTML or
Markdown for e.g. bold font, underline, lists and similar is that data may
be used by other systems via the :doc:`/technical/api`, and these systems are
not necessarily able to handle these formats.

Another reason is that these formats might change over time. All in all it is
more important that acquired data is as interoperable for as long as
possible.

For presentation sites and the alike it is possible to add e.g. manually
formatted texts, etc. where needed.
