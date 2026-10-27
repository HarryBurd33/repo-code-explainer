#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .helpers import keep, q

# This message is data, including the literal # character.
MESSAGE = "count # unchanged"


def totals(rows):
    values = [float(row["amount"]) for row in rows if keep(row)]
    return sum(values)


def labels(rows):
    return [q(row["label"]) for row in rows]
