import MendeleyHttpClient
import MendeleyRPC

import json
import time

import unittest

class OldApiClient():
    def __init__(self):
        self.oldClient = MendeleyRPC.MendeleyRPC("unused")

    class Value:
        def __init__(self, value):
            self.Value = value

    def request(self, functionName, argument):
        startTime = time.time()
        responseLength = self.oldClient.execute({0: self.Value(functionName + unichr(13) + argument)})
        response = self.oldClient.execute({0: self.Value("getStringResult")})
        print "old Api request: " + functionName + " took " + str(1000 * (time.time() - startTime)) + "ms"
        return response

class TestMendeleyHttpClient(unittest.TestCase):

    def setUp(self):
        self.client = MendeleyHttpClient.MendeleyHttpClient()
        self.oldClient = OldApiClient()
        # todo: tidy up first is "formattedText" and "citationCluster", second just "citationCluster"
        self.testClusters = [
            '{"formattedText": "(Evans & Jr, 2002; Smith & Jr, 2001)", "citationCluster": {"mendeley": {"previouslyFormattedCitation": "(Evans & Jr, 2002; Smith & Jr, 2001)"}, "citationItems": [{"uris": ["http://local/documents/?uuid=55ff8735-3f3c-4c9f-87c3-8db322ba3f74"], "id": "ITEM-1", "itemData": {"title": "Title01", "issued": {"date-parts": [["2001"]]}, "author": [{"given": "John", "family": "Smith"}, {"given": "John Smith", "family": "Jr"}], "note": "<m:note/>", "type": "article", "id": "ITEM-1"}}, {"uris": ["http://local/documents/?uuid=15d6d1e4-a9ff-4258-88b6-a6d6d6bdc0ed"], "id": "ITEM-2", "itemData": {"title": "Title02", "issued": {"date-parts": [["2002"]]}, "author": [{"given": "Gareth", "family": "Evans"}, {"given": "Gareth Evans", "family": "Jr"}], "note": "<m:note/>", "type": "article", "id": "ITEM-2"}}], "properties": {"noteIndex": 0}, "schema": "https://github.com/citation-style-language/schema/raw/master/csl-citation.json"}}',
            '{"mendeley": {"previouslyFormattedCitation": "(Evans & Jr, 2002; Smith & Jr, 2001)"}, "citationItems": [{"uris": ["http://local/documents/?uuid=55ff8735-3f3c-4c9f-87c3-8db322ba3f74"], "id": "ITEM-1", "itemData": {"title": "Title01", "issued": {"date-parts": [["2001"]]}, "author": [{"given": "John", "family": "Smith"}, {"given": "John Smith", "family": "Jr"}], "note": "<m:note/>", "type": "article", "id": "ITEM-1"}}, {"uris": ["http://local/documents/?uuid=15d6d1e4-a9ff-4258-88b6-a6d6d6bdc0ed"], "id": "ITEM-2", "itemData": {"title": "Title02", "issued": {"date-parts": [["2002"]]}, "author": [{"given": "Gareth", "family": "Evans"}, {"given": "Gareth Evans", "family": "Jr"}], "note": "<m:note/>", "type": "article", "id": "ITEM-2"}}], "properties": {"noteIndex": 0}, "schema": "https://github.com/citation-style-language/schema/raw/master/csl-citation.json"}'
            ]

    def test_simpleOldApiCall(self):
        userAccount = self.oldClient.request("getUserAccount", "")
        self.assertEqual(userAccount, "testDatabase@test.com@local")

    def test_simpleNewApiCall(self):
        response = self.client.userAccount()
        self.assertEqual(response.body.account, "testDatabase@test.com@local")

    def test_slowNewApiCalls(self):
        # this call should complete without requiring user interaction

        response1 = self.client.formattedCitationsAndBibliography_Interactive(
                "http://www.zotero.org/styles/apa",
                [
                    json.loads(self.testClusters[0]),
                    json.loads(self.testClusters[0])
                ]
                )

        # should get the same cluster1 back
        self.assertEqual(
                json.dumps(response1.body.citationClusters[0]),
                self.testClusters[0])

        # should get the same cluster2 back
        self.assertEqual(
                json.dumps(response1.body.citationClusters[1]),
                self.testClusters[0])

        response2 = self.client.formattedCitationsAndBibliography_Interactive(
                "http://www.zotero.org/styles/apa", 
                [
                    {
                        "citationCluster":json.loads(self.testClusters[1])
                    }
                ]
                )

        self.assertEqual(
                json.dumps(response1.body.citationClusters[0]["citationCluster"]),
                self.testClusters[1])
        
        self.assertEqual(
                response1.body.citationClusters[0]["formattedText"],
                "(Evans & Jr, 2002; Smith & Jr, 2001)")

        # for now the bibliography is written to a temp file, this may change in future
        bibliography = open(response1.body.bibliography).read()
        self.assertEqual(
                bibliography,
                '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml"><head>\n<meta http-equiv="Content-Type" content="text/html;charset=utf-8" /><title></title>\n</head>\n<body>\n&nbsp;<p>\n<p style=\'margin-left:24pt;text-indent:-24.0pt\'>Evans, G., &#38; Jr, G. E. (2002). Title02.</p><p style=\'margin-left:24pt;text-indent:-24.0pt\'>Smith, J., &#38; Jr, J. S. (2001). Title01.</p>\n</p></body></html>\n'
                )

    def test_styleName_getFromUrl(self):
        response = self.client.styleName_getFromUrl(
                {"citationStyleUrl": "http://www.zotero.org/styles/apa"})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body.citationStyleName, "American Psychological Association 6th Edition")

    def test_bringPluginToForeground(self):
        response = self.client.bringPluginToForeground()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body.success, True)

    def test_citationStyles_default(self):
        response = self.client.citationStyles_default()
        self.assertEqual(response.status, 200)
        self.assertEqual(len(response.body.citationStyles), 10)
        
        self.assertTrue(len(response.body.citationStyles[0]["title"]) > 0)
        self.assertTrue(len(response.body.citationStyles[0]["url"]) > 0)

    def test_citations_merge(self):
        response = self.client.citations_merge(
            {"citationClusters":
                [
                    {"citationCluster": json.loads(self.testClusters[0])},
                    {"citationCluster": json.loads(self.testClusters[1])}
                ]
            })
        self.assertEqual(response.status, 200)
        self.assertEqual(json.dumps(response.body.citationCluster),
            '{"mendeley": {}, "citationItems": [{"itemData": {"title": "Title01", "issued": {"date-parts": [["2001"]]}, "author": [{"given": "John", "family": "Smith"}, {"given": "John Smith", "family": "Jr"}], "note": "<m:note/>", "type": "article", "id": "ITEM-1"}, "title": "Title01", "issued": {"date-parts": [["2001"]]}, "author": [{"given": "John", "family": "Smith"}, {"given": "John Smith", "family": "Jr"}], "uris": ["http://unknownServer/documents/?uuid=55ff8735-3f3c-4c9f-87c3-8db322ba3f74"], "note": "<m:note/>", "type": "article", "id": "ITEM-1"}, {"itemData": {"title": "Title02", "issued": {"date-parts": [["2002"]]}, "author": [{"given": "Gareth", "family": "Evans"}, {"given": "Gareth Evans", "family": "Jr"}], "note": "<m:note/>", "type": "article", "id": "ITEM-2"}, "title": "Title02", "issued": {"date-parts": [["2002"]]}, "author": [{"given": "Gareth", "family": "Evans"}, {"given": "Gareth Evans", "family": "Jr"}], "uris": ["http://unknownServer/documents/?uuid=15d6d1e4-a9ff-4258-88b6-a6d6d6bdc0ed"], "note": "<m:note/>", "type": "article", "id": "ITEM-2"}], "properties": {"noteIndex": 0}, "schema": "https://github.com/citation-style-language/schema/raw/master/csl-citation.json"}')

    def test_citation_undoManualFormat(self):
        citation = json.loads(self.testClusters[0])["citationCluster"]
        citation["mendeley"]["manualFormat"] = "Test manual format"
        self.assertTrue("manualFormat" in citation["mendeley"])
        response = self.client.citation_undoManualFormat(citation)
        self.assertEqual(response.status, 200)
        self.assertFalse("manualFormat" in response.body.citationCluster["mendeley"])
        
    def test_wordProcessor_set(self):
        response = self.client.wordProcessor_set(
            {
                "wordProcessor": "test processor",
                "version": 999
            })

        self.assertEqual(response.status, 200)

if __name__ == '__main__':
    unittest.main()