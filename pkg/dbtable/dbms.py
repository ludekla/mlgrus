from typing import Callable, List, Dict, Any, Callable
from collections import defaultdict


class Table:
    '''Database table'''
    def __init__(self, columns: List[str], types: List[type]) -> None:
        assert len(columns) == len(types)
        self.columns = columns # names of the columns
        self.types = types     # types of the columns
        self.rows = []         # List[Row] where Row = Dict[str, Any]

    def __repr__(self):
        if len(self) > 20:
            rows = '\n '.join(str(row) for row in self.rows[:20]) + '\n ...'
        else:
            rows = '\n '.join(str(row) for row in self.rows)
        return f'Table(\n {self.columns}\n {rows}\n)'

    def __getitem__(self, idx: int):
        '''Returns a Row'''
        return self.rows[idx]

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)

    def col2type(self, col: str) -> type:
        '''helper method to get the type of a column'''
        return self.types[self.columns.index(col)]

    def insert(self, values: list) -> None:
        # basic checks before insertion
        if len(values) != len(self.types):
            raise ValueError(f'Please provide {len(self.types)} values')
        for value, typ in zip(values, self.types):
            if not isinstance(value, typ):
                raise TypeError(f'Expected type {typ} but got {value}')
        self.rows.append(dict(zip(self.columns, values)))

    def update(self, updates: Dict[str, Any], predicate: Callable = lambda row: True):
        # basic checks before updating
        for col, val in updates.items():
            if col not in self.columns:
                raise TypeError(f'Invalid column: {col}')
            typ = self.col2type(col)
            if not isinstance(val, typ) and val is not None:
                raise TypeError(f'Expected type {typ} but got {val}')
        for row in self.rows:
            if predicate(row):
                for col, val in updates.items():
                    row[col] = val

    def delete(self, predicate: Callable = lambda row: True):
        purgees = [row for row in self.rows if predicate(row)]
        for purgee in purgees:
            self.rows.remove(purgee)

    def select(self, 
        keep_cols: List[str] = None, 
        additional_cols: Dict[str, Callable] = None
    ):
        if keep_cols is None:
            keep_cols = self.columns
        if additional_cols is None:
            additional_cols = {}
        new_cols = keep_cols + list(additional_cols.keys())
        keep_types = [self.col2type(col) for col in keep_cols]
        add_types = [calc.__annotations__['return'] for calc in additional_cols.values()]
        # create a new table for the results
        tb = Table(new_cols, keep_types + add_types)
        for row in self.rows:
            new_row = [row[col] for col in keep_cols]
            for calc in additional_cols.values():
                new_row.append(calc(row))
            tb.insert(new_row)
        return tb

    def where(self, predicate: Callable = lambda row: True):
        ''''Return only those rows that satisfy the predicate'''
        tb = Table(self.columns, self.types)
        for row in self.rows:
            if predicate(row):
                values = [row[col] for col in self.columns]
                tb.insert(values)
        return tb

    def limit(self, nrows: int):
        ''''Return only the top nRows rows'''
        tb = Table(self.columns, self.types)
        for i, row in enumerate(self.rows, 1):
            if i > nrows:
                break
            values = [row[col] for col in self.columns]
            tb.insert(values)
        return tb

    def groupby(self,
        groupby_cols: List[str],
        aggregates: Dict[str, Callable],
        having: Callable = lambda group: True
    ):
        grouped_rows = defaultdict(list)
        for row in self.rows:
            key = tuple(row[col] for col in groupby_cols)
            grouped_rows[key].append(row)
        newcols = groupby_cols + list(aggregates.keys())
        groupby_types = [self.col2type(col) for col in groupby_cols]
        aggregate_types = [
            agg.__annotations__['return'] for agg in aggregates.values()
        ]
        tb = Table(newcols, groupby_types + aggregate_types)
        for key, rows in grouped_rows.items():
            if having(rows):
                newrow = list(key)
                for agg_name, agg_fn in aggregates.items():
                    newrow.append(agg_fn(rows))
                tb.insert(newrow)
        return tb

    def orderby(self, order: Callable) -> 'Table':
        tb = self.select()  # copy
        tb.rows.sort(key=order)
        return tb

    def join(self, other_table: 'Table', left_join=False) -> 'Table':
        # columns of both tables
        join_on_cols = [c for c in self.columns if c in other_table.columns]
        # columns only of right table
        additional_cols = [c for c in other_table.columns if c not in join_on_cols]
        # columns of left table and additional columns from right table
        newcols = self.columns + additional_cols
        newtypes = self.types + [other_table.col2type(c) for c in additional_cols]
        jtb = Table(newcols, newtypes)  # join table
        for row in self.rows:
            isjoin = lambda orow: all(orow[c] == row[c] for c in join_on_cols)
            other_rows = other_table.where(isjoin).rows
            # each other row that matches in the join-on columns produces a result row
            for orow in other_rows:
                jtb.insert(
                    [row[c] for c in self.columns] + [orow[c] for c in additional_cols]
                )
            if left_join and len(other_rows) == 0:
                jtb.insert(
                    [row[c] for c in self.columns] + ['' for _ in additional_cols]
                )
        return jtb

def min_userid(rows) -> int:
    return min(row['userID'] for row in rows)

def length(rows) -> int:
    return len(rows)

def first_letter(row) -> str:
    return row['name'][0] if row['name'] else ''

def avg_nfriends(rows) -> float:
    return sum(row['nfriends'] for row in rows) / len(rows)

def enough_friends(rows) -> bool:
    return avg_nfriends(rows) > 1

def sum_userids(rows) -> int:
    return sum(row['userID'] for row in rows)

def count_interests(rows) -> int:
    '''Counts the number of rows with entries in interests columns'''
    return len([row for row in rows if row['interest']])


if __name__ == '__main__':

    '''
    CREATE TABLE users (
        userID INT NOT NULL,
        name VARCHAR(200),
        nfriends INT    
    );
    '''
    users = Table(['userID', 'name', 'nfriends'], [int, str, int])
    data = [
        [0, "Hero", 0],
        [1, "Dunn", 2],
        [2, "Sue", 3],
        [3, "Chi", 3],
        [4, "Thor", 3],
        [5, "Clive", 2],
        [6, "Hicks", 3],
        [7, "Devin", 2],
        [8, "Kate", 2],
        [9, "Klein", 3],
        [10, "Jen", 1]
    ]
    for row in data:
        users.insert(row)
    print('created:\n', users)

    print('before update:', users[1])
    '''
    UPDATE users
    SET nfriends = 3
    WHERE userID = 1;
    '''
    users.update({'nfriends': 3}, predicate=lambda row: row['userID'] == 1)
    print('after update:', users[1])
    '''
    SELECT userID FROM users WHERE name = 'Dunn';
    '''
    dunn_ids = (
        users
        .where(lambda row: row['name'] == 'Dunn')
        .select(keep_cols=['userID'])
    )
    print('dunn ids:\n', dunn_ids)
    '''
    DELETE FROM users WHERE userID = 1;
    '''
    users.delete(lambda row: row['userID'] == 1)
    print('delete:\n', users)
    '''
    SELECT * FROM users;
    '''
    alldata = users.select()
    print('all data:\n', alldata)
    '''
    SELECT userID FROM users;
    '''
    ids = users.select(keep_cols=['userID', 'name'])
    print('select ids:\n', ids)
    '''
    SELECT LENGTH(name) AS nameLen FROM users;
    '''
    def name_len(row) -> int: return len(row['name'])
    lens = users.select(keep_cols=[], additional_cols={'nameLen': name_len})
    '''
    SELECT * FROM users LIMIT 4;
    '''
    four = users.limit(4)
    '''
    SELECT 
        LENGTH(name) AS name_len,
        MIN(userID) AS min_userID,
        COUNT(*) AS nUsers
    FROM users
    GROUP BY LENGTH(name);
    '''
    stats_by_len = (
        users
        .select(additional_cols={'name_len': name_len})
        .groupby(
            groupby_cols=['name_len'], 
            aggregates={'min_userid': min_userid, 'nusers': length} 
        )
    )
    print(stats_by_len)
    '''
    SELECT SUM(userID) AS userid
    FROM users
    WHERE userID > 1;
    '''
    userid_sum = (
        users
        .where(lambda row: row['userID'] > 1)
        .groupby(groupby_cols=[], aggregates={'userid_sum': sum_userids})
    )
    print(userid_sum)
    '''
    SELECT 
        SUBSTR(name, 1, 1) AS first_letter,
        AVG(nfriends) AS avg_nfriends
    FROM users
    GROUP BY SUBSTR(name, 1, 1)
    HAVING AVG(nfriends) > 1;
    '''
    avg_by_letter = (
        users
        .select(additional_cols={'first_letter': first_letter})
        .groupby(
            groupby_cols=['first_letter'], 
            aggregates={'avg_nfriends': avg_nfriends},
            having=enough_friends
        )
    )
    ''''
    SELECT * FROM users
    ORDER BY name
    LIMIT 4;
    '''
    friendliest = (
        avg_by_letter
        .orderby(order=lambda row: -row['avg_nfriends'])
        .limit(4)
    )
    '''
    CREATE TABLE user_interests (
        userID INT NOT NULL,
        interest VARCHAR(100) NOT NULL 
    )
    '''
    user_interests = Table(['userID', 'interest'], [int, str])
    user_interests.insert([0, 'SQL'])
    user_interests.insert([0, 'NoSQL'])
    user_interests.insert([2, 'SQL'])
    user_interests.insert([2, 'MySQL'])
    '''
    SELECT * FROM users
    LEFT JOIN user_interests
    ON users.userID = user_interests.userID
    '''
    joined = users.join(user_interests, left_join=True)
    '''
    SELECT users.name
    FROM users
    JOIN user_interests
    ON users.userID = user_interests.userID
    WHERE user_interests.interest = 'SQL'
    '''
    sql_users = (
        users
        .join(user_interests)
        .where(lambda row: row['interest'] == 'SQL')
        .select(keep_cols=['name'])
    )
    '''
    SELECT users.userID, COUNT(user_interests.interest) AS ninterests
    FROM users
    LEFT JOIN user_interests
    ON users.userID = user_interests.userID
    '''
    user_interest_counts = (
        users
        .join(user_interests, left_join=True)
        .groupby(groupby_cols=['userID'], aggregates={'ninterests': count_interests})
    )
    ''''
    SELECT MIN(userID) AS min_userID 
    FROM (SELECT userID FROM user_interests WHERE interests = 'SQL') sql_interests;
    '''
    sql_ids = (
        user_interests
        .where(lambda row: row['interest'] == 'SQL')
        .select(keep_cols=['userID'])
    )
    ids = sql_ids.groupby(groupby_cols=[], aggregates={'minUserIds': min_userid})
