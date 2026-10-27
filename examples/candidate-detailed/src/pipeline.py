#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Import keep (enabled truthiness) and q (sequence reversal) from helpers.
from .helpers import keep, q

# This message is data, including the literal # character.
MESSAGE = "count # unchanged"


# Sum numeric amounts of accepted rows; helpers.keep decides which rows count.
def totals(rows):
    # Visit rows in order, accepting truthy enabled fields; absent means False.
    # Convert required amounts to floats; missing keys or invalid numbers raise.
    values = [float(row["amount"]) for row in rows if keep(row)]
    # Add the converted amounts; no accepted rows yields integer 0.
    return sum(values)


# Produce reversed labels in the same order as the supplied rows.
def labels(rows):
    # Read each required label and reverse it with value[::-1] in helpers.q.
    # Missing labels or values that cannot be sliced raise errors.
    return [q(row["label"]) for row in rows]
