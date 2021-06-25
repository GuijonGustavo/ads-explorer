"""
Script to do something with the list of papers
"""

import itertools
import ads
from metaphone import doublemetaphone
import numpy as np
import pandas as pd


class PapersManager:
    """
    Manager of a list of papers

    Attributes
    ----------
    paper_list : list
        Resulting paper list by SearchQuery method of ADS package

    Methods
    -------
    TBW
    """

    def __init__(self, papers_list):
        """
        Parameters
        ----------
        papers_list : list
             List of papers
        """
        self.papers_list = papers_list
        self.papers_df = self.make_pandas()
        self.lookup_dict = ({}, {})
        self.set_lookup_dir()

    def make_pandas(self):
        """
        make a pandas dataframe from a papers list
        """
        columns = self.papers_list[0]._raw.keys()
        papers_df = pd.DataFrame(columns=columns)
        for paper in self.papers_list:
            papers_df = papers_df.append(paper._raw, ignore_index=True)
        # papers_df.set_index('id', inplace=True)
        return papers_df

    def add_combinations_to_directory(self, name_tuple_list, person_id):
        """
        Add all the combinations for a name to the lookup directory
        """
        for name_tuple in name_tuple_list:
            concat_name = generate_normalized_name(name_tuple)
            metaphone_tuple = doublemetaphone(concat_name)
            if metaphone_tuple[0] in self.lookup_dict[0]:
                if not person_id in self.lookup_dict[0][metaphone_tuple[0]]:
                    self.lookup_dict[0][metaphone_tuple[0]].append(person_id)
            else:
                self.lookup_dict[0][metaphone_tuple[0]] = [person_id]
            if metaphone_tuple[1] in self.lookup_dict[1]:
                if not person_id in self.lookup_dict[1][metaphone_tuple[1]]:
                    self.lookup_dict[1][metaphone_tuple[1]].append(person_id)
            else:
                self.lookup_dict[1][metaphone_tuple[1]] = [person_id]

    def add_person_to_lookup_directory(self, person_id, name_tuple):
        """
        Add a person id (paper id) and the name to the lookup directory
        """
        combs = generate_combinations(name_tuple)
        self.add_combinations_to_directory(combs, person_id)

    def match_name(self, name_tuple):
        """
        Check if a name is on the lookup directory and returns the match list
        """
        match_list = []
        combinations = generate_combinations(name_tuple)
        for comb_tuple in combinations:
            concat_name = generate_normalized_name(comb_tuple)
            metaphone_tuple = doublemetaphone(concat_name)
            if metaphone_tuple[0] in self.lookup_dict[0]:
                match_list.append(
                    (concat_name, self.lookup_dict[0][metaphone_tuple[0]]))
        # Iterate through all matches and check for single result tuples
        # Ensure that the singe result tuples are pointing to the same id
        # If not or no single result tuple exists, return 'None'
        unique_id = None
        for match_tuple in match_list:
            if len(match_tuple[1]) == 1:
                if unique_id is not None:
                    if unique_id != match_tuple[1][0]:
                        unique_id = None
                        break
                else:
                    unique_id = match_tuple[1][0]
        return unique_id, match_list

    def set_lookup_dir(self):
        """
        Set lookup directory for author search
        """
        for i in range(len(self.papers_df)):
            row = self.papers_df.iloc[i]
            authors = row['author']
            id_paper = row.name
            for author in authors:
                author_c = [normalize(word.strip('.,'))
                            for word in author.split(' ')]
                self.add_person_to_lookup_directory(id_paper, author_c)

    def search_author(self, names):
        """
        Search name(s) in the abstract

        Parameters
        ----------
        names : str or list
            name or list of names to search in the paper list

        """
        if isinstance(names, str):
            name_tuple = normalize(names).split(' ')
            _, match_list = self.match_name(name_tuple)
            match_id = []
            for elem in match_list:
                match_id += elem[1]
        else:
            match_id = []
            for name in names:
                name_tuple = normalize(name).split(' ')
                _, match_list = self.match_name(name_tuple)
                for elem in match_list:
                    match_id += elem[1]
        match_id_set = set(match_id)
        if len(match_id_set) != 0:
            papers_list = [self.papers_list[i] for i in match_id_set]
            return PapersManager(papers_list)
        else:
            print('Not match found')
            return None
        # return self.papers_df.loc[match_id_set]

    def search_word(self, words, logical_op='and'):
        """
        Search word(s) in the abstract

        Parameters
        ----------
        words : str or list
            Word or list of words to search in abstract

        logical_op : str
            Logical operation for a list of words, defaul:'and'
        """
        if 'abstract' not in self.papers_df.columns:
            print('No abstract field found')
            return None
        if isinstance(words, str):
            mask = self.papers_df['abstract'].str.contains(words,
                                                           case=False)
        else:
            masks = [[self.papers_df['abstract'].str.contains(word,
                                                              case=False)]
                     for word in words]
            mask = np.ones_like(masks[0][0])
            if logical_op == 'and':
                for submask in masks:
                    mask = mask & submask[0]
            elif logical_op == 'or':
                for submask in masks:
                    mask = mask | submask
        if not mask.sum() == 0:
            papers_list = []
            for i, val in enumerate(mask):
                if val:
                    papers_list.append(self.papers_list[i])
            return PapersManager(papers_list)
        else:
            print('Not match found')
            return None
        # return self.papers_df.loc[mask]

    def search_year(self, years):
        """
        Search papers by year
        """
        if isinstance(years, int):
            mask = self.papers_df['year'].values == str(years)
        else:
            masks = [self.papers_df['year'].values == str(year)
                     for year in years]
            print(masks)
            mask = np.zeros_like(masks[0][0])
            for submask in masks:
                mask = mask | submask
        if not mask.sum() == 0:
            papers_list = []
            for i, val in enumerate(mask):
                if val:
                    papers_list.append(self.papers_list[i])
            return PapersManager(papers_list)
        else:
            print('Not match found')
            return None
        # return self.papers_df.loc[mask]

    def get_author_set(self):
        """
        Get author set from the papers list
        """
        if 'author' not in self.papers_df.columns:
            print('No author field found')
            return None
        authors_list = [author
                        for row in self.papers_df['author'].iteritems()
                        for author in row[1]]
        authors_list_clean = [normalize(author) for author in authors_list]
        authors_set = set(authors_list_clean)
        return authors_set

    def custom_output(self, fields, explicit=[], auth_num=None):
        """
        Generates a custom output in a particular format
        """
        if fields is None:
            print('No output fields specified, no output generated')
            return
        datafr = self.papers_df
        if isinstance(fields, str):
            for elem in list(datafr[fields]):
                print(f'· {elem[0]}')
        else:
            for kel in range(len(list(datafr[fields[0]]))):
                for kf in range(len(fields)):
                    elem = datafr[fields[kf]][kel]
                    if fields[kf] in explicit:
                        fname = fields[kf]+': '
                    else:
                        fname = ''
                    if isinstance(elem, list):
                        if len(elem) == 1:
                            print(f'{fname}{elem[0]}')
                        else:
                            print(fname+', '.join(elem))
                    else:
                        print(f'{fname}{elem}')
                    # print(datafr[fields[kf]][kel])
                    # print('')
                print('\n')

    def add_paper(self, bibcode):
        """
        Add a paper to the database
        """
        fl = ['abstract', 'author', 'id', 'year',
              'ack', 'aff', 'alternate_bibcode', 'alternate_title',
              'arxiv_class', 'citation_count', 'bibcode', 'bibgroup',
              'copyright', 'data', 'database', 'doctype', 'doi', 'identifier',
              'indexstamp', 'first_author', 'grant', 'issue', 'keyword',
              'page', 'property', 'pub', 'pubdate', 'read_count', 'reference',
              'citation', 'title', 'vizier', 'volume', 'orcid_pub',
              'orcid_user', 'orcid_other', 'metrics', 'bibtex']
        new_paper = list(ads.SearchQuery(bibcode=bibcode, fl=fl))
        self.papers_list += new_paper
        self.papers_df = self.make_pandas()
        self.lookup_dict = ({}, {})
        self.set_lookup_dir()

    def remove_paper(self, bibcode):
        """
        Remove a paper to the database
        """
        mask = self.papers_df.bibcode == bibcode
        idx = (self.papers_df.index[mask]).values[0]
        self.papers_list.pop(idx)
        self.papers_df = self.make_pandas()
        self.lookup_dict = ({}, {})
        self.set_lookup_dir()


def normalize(string):
    """
    Replace words with accent mark
    """
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("à", "a"),
        ("è", "e"),
        ("ù", "u"),
    )
    for vowel_w_acc, vowel_wo_acc in replacements:
        string = string.replace(vowel_w_acc,
                                vowel_wo_acc).replace(vowel_w_acc.upper(),
                                                      vowel_wo_acc.upper())
    return string


def clean_author_list(author_list):
    """
    Clean author list from duplicate entry
    """
    author_list_clean = [normalize(author) for author in author_list]
    return set(author_list_clean)


def generate_normalized_name(name_tuple):
    """
    Generates a normalized name (without whitespaces and lowercase)
    """
    name_arr = list(name_tuple)
    name_arr.sort()
    name_str = ''.join(name_arr)
    return name_str.lower()


def generate_combinations(name_tuple):
    """
    Generates all the possible combinations for a name
    """
    perms = []
    perms.append(name_tuple)
    i = len(list(name_tuple))-1
    while i > 0:
        perms.extend(itertools.combinations(name_tuple, i))
        i -= 1
    return perms
