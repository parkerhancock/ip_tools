"""Hand-crafted Shift-JIS ZIP fixtures for the JPO document-bundle parser.

These match the schemas observed in production JPO bundles (see
:mod:`patent_client_agents.jpo.documents`). Kept small enough to be
read at a glance — a real bundle's body text would be hundreds of
lines of Japanese.
"""

from __future__ import annotations

import io
import zipfile

# A complete, parseable applicant-filed opinion (意見書).
APPLICATION_OPINION_XML = b"""<?xml version="1.0" encoding="Shift_JIS"?>
<!DOCTYPE jp:pat-rspns PUBLIC "-//JPO//DTD PATENT RESPONCE DOCUMENT 1.0//EN" "pat-rspn.dtd" []>
<jp:pat-rspns lang="ja" dtd-version="1.0" xmlns:jp="http://www.jpo.go.jp">
<jp:response-a53 jp:kind-of-law="patent">
<jp:document-code>A153</jp:document-code>
<jp:addressed-to-person>\x93\xc1\x8b\x96\x92\xa1\x90R\x8d\xb8\x8a\xaf</jp:addressed-to-person>
<jp:indication-of-case-article>
<jp:application-reference appl-type="application" jp:kind-of-law="patent">
<jp:document-id>
<jp:doc-number>2020999999</jp:doc-number>
</jp:document-id>
</jp:application-reference>
</jp:indication-of-case-article>
<jp:applicants>
<jp:applicant>
<jp:addressbook>
<jp:name>\x83e\x83X\x83g\x95@\x90l</jp:name>
<jp:registered-number>000999999</jp:registered-number>
</jp:addressbook>
</jp:applicant>
</jp:applicants>
<jp:agents>
<jp:agent jp:kind-of-agent="representative">
<jp:addressbook>
<jp:name>\x83e\x83X\x83g\x91\xe3\x97\x9d\x90l</jp:name>
</jp:addressbook>
</jp:agent>
</jp:agents>
<jp:dispatch-number>012345</jp:dispatch-number>
<jp:opinion-contents-article><p num="">
\x83e\x83X\x83g\x82\xcc\x88\xd3\x8c\xa9\x82\xc5\x82\xb7\x81B
</p></jp:opinion-contents-article>
</jp:response-a53>
</jp:pat-rspns>
"""

# A mailed notice of refusal (\x8b\x91\x90\xe2\x97\x9d\x97R\x92\xca\x92m\x8f\x91 = 拒絶理由通知書).
MAILED_NOTICE_OF_REFUSAL_XML = b"""<?xml version="1.0" encoding="Shift_JIS"?>
<!DOCTYPE jp:notice-pat-exam-rn PUBLIC "-//JPO//DTD NOTICE DOCUMENT BY PATENT SUBSTANTIAL EXAMINATION RENEWAL 1.0//EN" "ntc-pt-e-rn.dtd" []>
<jp:notice-pat-exam-rn lang="ja" dtd-version="1.0" xmlns:jp="http://www.jpo.go.jp">
<jp:notice-of-rejection-a131-rn jp:kind-of-law="patent">
<jp:document-name>\x8b\x91\x90\xe2\x97\x9d\x97R\x92\xca\x92m\x8f\x91</jp:document-name>
<jp:bibliog-in-ntc-pat-exam-rn>
<jp:application-reference appl-type="application" jp:kind-of-law="patent">
<jp:document-id>
<jp:doc-number>2020999999</jp:doc-number>
</jp:document-id>
</jp:application-reference>
<jp:drafting-date>
<jp:date>20240101</jp:date>
</jp:drafting-date>
<jp:draft-person-group>
<jp:name>\x83e\x83X\x83g\x90R\x8d\xb8\x8a\xaf</jp:name>
<jp:staff-code>0001</jp:staff-code>
</jp:draft-person-group>
<jp:article-group>
<jp:article>\x91\xe629\x8f\xf0\x91\xe61\x8d\x80\x91\xe63\x8d\x86</jp:article>
<jp:article>\x91\xe629\x8f\xf0\x91\xe62\x8d\x80</jp:article>
</jp:article-group>
</jp:bibliog-in-ntc-pat-exam-rn>
<jp:conclusion-part-article>
<p num="">\x82\xb1\x82\xcc\x8fo\x8a\xe8\x82\xcd\x91\xe629\x8f\xf0\x88\xe1\x94\xbd\x82\xc5\x82\xb7\x81B</p>
</jp:conclusion-part-article>
</jp:notice-of-rejection-a131-rn>
</jp:notice-pat-exam-rn>
"""


def make_application_bundle_zip() -> bytes:
    """Build an in-memory ZIP matching JPO's application-documents layout."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("A53_99900012345/JPOXMLDOC01-jpbibl.xml", APPLICATION_OPINION_XML)
        # Include a binary attachment that the parser should list but not
        # try to decode.
        zf.writestr("A53_99900012345/exhibit.jpg", b"\xff\xd8\xff\xe0FAKEJPEG")
    return buf.getvalue()


def make_mailed_bundle_zip() -> bytes:
    """Build an in-memory ZIP matching JPO's mailed-documents layout."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("00012345-jpntce.xml", MAILED_NOTICE_OF_REFUSAL_XML)
    return buf.getvalue()


def make_refusal_bundle_zip() -> bytes:
    """Build an in-memory ZIP for the refusal-notices layout (subset of mailed)."""
    return make_mailed_bundle_zip()


def make_invalid_xml_bundle_zip() -> bytes:
    """Build a ZIP with a malformed XML index — exercises the parse_error path."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("00099999-jpntce.xml", b"<?xml version='1.0'?><not-closed>")
    return buf.getvalue()


__all__ = [
    "make_application_bundle_zip",
    "make_mailed_bundle_zip",
    "make_refusal_bundle_zip",
    "make_invalid_xml_bundle_zip",
]
