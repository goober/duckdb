from multiprocessing.sharedctypes import Value
import numpy
import datetime
import pandas
import pytest
import duckdb
from io import StringIO, BytesIO

def TestFile(name):
	import os
	filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','data',name)
	return filename

class TestReadCSV(object):
	def test_using_connection_wrapper(self):
		rel = duckdb.read_csv(TestFile('category.csv'))
		res = rel.fetchone()
		print(res)
		assert res == (1, 'Action', datetime.datetime(2006, 2, 15, 4, 46, 27))

	def test_using_connection_wrapper_with_keyword(self):
		rel = duckdb.read_csv(TestFile('category.csv'), dtype={'category_id': 'string'})
		res = rel.fetchone()
		print(res)
		assert res == ('1', 'Action', datetime.datetime(2006, 2, 15, 4, 46, 27))

	def test_no_options(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'))
		res = rel.fetchone()
		print(res)
		assert res == (1, 'Action', datetime.datetime(2006, 2, 15, 4, 46, 27))

	def test_dtype(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), dtype={'category_id': 'string'})
		res = rel.fetchone()
		print(res)
		assert res == ('1', 'Action', datetime.datetime(2006, 2, 15, 4, 46, 27))

	def test_dtype_as_list(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), dtype=['string'])
		res = rel.fetchone()
		print(res)
		assert res == ('1', 'Action', datetime.datetime(2006, 2, 15, 4, 46, 27))

		rel = duckdb_cursor.read_csv(TestFile('category.csv'), dtype=['double'])
		res = rel.fetchone()
		print(res)
		assert res == (1.0, 'Action', datetime.datetime(2006, 2, 15, 4, 46, 27))

	def test_sep(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), sep=" ")
		res = rel.fetchone()
		print(res)
		assert res == ('1|Action|2006-02-15', datetime.time(4, 46, 27))

	def test_delimiter(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), delimiter=" ")
		res = rel.fetchone()
		print(res)
		assert res == ('1|Action|2006-02-15', datetime.time(4, 46, 27))

	def test_delimiter_and_sep(self, duckdb_cursor):
		with pytest.raises(duckdb.InvalidInputException, match="read_csv takes either 'delimiter' or 'sep', not both"):
			rel = duckdb_cursor.read_csv(TestFile('category.csv'), delimiter=" ", sep=" ")

	def test_header_true(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), header=True)
		res = rel.fetchone()
		print(res)
		assert res == (1, 'Action', datetime.datetime(2006, 2, 15, 4, 46, 27))

	@pytest.mark.skip(reason="Issue #6011 needs to be fixed first, header=False doesn't work correctly")
	def test_header_false(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), header=False)

	def test_na_values(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), na_values='Action')
		res = rel.fetchone()
		print(res)
		assert res == (1, None, datetime.datetime(2006, 2, 15, 4, 46, 27))

	def test_skiprows(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), skiprows=1)
		res = rel.fetchone()
		print(res)
		assert res == (1, 'Action', datetime.datetime(2006, 2, 15, 4, 46, 27))

	# We want to detect this at bind time
	def test_compression_wrong(self, duckdb_cursor):
		with pytest.raises(duckdb.Error, match="Input is not a GZIP stream"):
			rel = duckdb_cursor.read_csv(TestFile('category.csv'), compression='gzip')

	def test_quotechar(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('unquote_without_delimiter.csv'), quotechar="")
		res = rel.fetchone()
		print(res)
		assert res == ('"AAA"BB',)

	def test_escapechar(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('quote_escape.csv'), escapechar=";")
		res = rel.limit(1,1).fetchone()
		print(res)
		assert res == ('345', 'TEST6', '"text""2""text"')

	def test_encoding_wrong(self, duckdb_cursor):
		with pytest.raises(duckdb.BinderException, match="Copy is only supported for UTF-8 encoded files, ENCODING 'UTF-8'"):
			rel = duckdb_cursor.read_csv(TestFile('quote_escape.csv'), encoding=";")

	def test_encoding_correct(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('quote_escape.csv'), encoding="UTF-8")
		res = rel.limit(1,1).fetchone()
		print(res)
		assert res == (345, 'TEST6', 'text"2"text')

	def test_parallel_true(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), parallel=True)
		res = rel.fetchone()
		print(res)
		assert res == (1, 'Action', datetime.datetime(2006, 2, 15, 4, 46, 27))

	def test_parallel_true(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), parallel=False)
		res = rel.fetchone()
		print(res)
		assert res == (1, 'Action', datetime.datetime(2006, 2, 15, 4, 46, 27))

	def test_date_format_as_datetime(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('datetime.csv'), date_format='%m/%d/%Y')
		res = rel.fetchone()
		print(res)
		assert res == (123, 'TEST2', datetime.time(12, 12, 12), datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 1, 12, 12))

	def test_date_format_as_date(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('datetime.csv'), date_format='%Y-%m-%d')
		res = rel.fetchone()
		print(res)
		assert res == (123, 'TEST2', datetime.time(12, 12, 12), datetime.date(2000, 1, 1), datetime.datetime(2000, 1, 1, 12, 12))

	def test_timestamp_format(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('datetime.csv'), timestamp_format='%m/%d/%Y')
		res = rel.fetchone()
		print(res)
		assert res == (123, 'TEST2', datetime.time(12, 12, 12), datetime.date(2000, 1, 1), '2000-01-01 12:12:00')

	def test_sample_size_incorrect(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('problematic.csv'), header=True, sample_size=1)
		with pytest.raises(duckdb.InvalidInputException):
			# The sniffer couldn't detect that this column contains non-integer values
			while True:
				res = rel.fetchone()
				if res is None:
					break

	def test_sample_size_correct(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('problematic.csv'), header=True, sample_size=-1)
		res = rel.fetchone()
		print(res)
		assert res == ('1', '1', '1')

	def test_all_varchar(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), all_varchar=True)
		res = rel.fetchone()
		print(res)
		assert res == ('1', 'Action', '2006-02-15 04:46:27')

	def test_normalize_names(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), normalize_names=False)
		df = rel.df()
		column_names = list(df.columns.values)
		# The names are not normalized, so they are capitalized
		assert 'CATEGORY_ID' in column_names

		rel = duckdb_cursor.read_csv(TestFile('category.csv'), normalize_names=True)
		df = rel.df()
		column_names = list(df.columns.values)
		# The capitalized names are normalized to lowercase instead
		assert 'CATEGORY_ID' not in column_names

	def test_filename(self, duckdb_cursor):
		rel = duckdb_cursor.read_csv(TestFile('category.csv'), filename=False)
		df = rel.df()
		column_names = list(df.columns.values)
		# The filename is not included in the returned columns
		assert 'filename' not in column_names

		rel = duckdb_cursor.read_csv(TestFile('category.csv'), filename=True)
		df = rel.df()
		column_names = list(df.columns.values)
		# The filename is included in the returned columns
		assert 'filename' in column_names

	def test_read_filelike(self, duckdb_cursor):
		string = StringIO("c1,c2,c3\na,b,c")
		res = duckdb_cursor.read_csv(string, header=True).fetchall()
		assert res == [('a', 'b', 'c')]

	def test_read_filelike_rel_out_of_scope(self, duckdb_cursor):
		def keep_in_scope():
			string = StringIO("c1,c2,c3\na,b,c")
			# Create a ReadCSVRelation on a file-like object
			# this will add the object to our internal object filesystem
			rel = duckdb_cursor.read_csv(string, header=True)
			# The file-like object will still exist, so we can execute this later
			return rel
		
		def close_scope():
			string = StringIO("c1,c2,c3\na,b,c")
			# Create a ReadCSVRelation on a file-like object
			# this will add the object to our internal object filesystem
			res = duckdb_cursor.read_csv(string, header=True).fetchall()
			# When the relation goes out of scope - we delete the file-like object from our filesystem
			return res

		relation = keep_in_scope()
		res = relation.fetchall()

		res2 = close_scope()
		assert res == res2

	def test_filelike_bytesio(self, duckdb_cursor):
		string = BytesIO(b"c1,c2,c3\na,b,c")
		res = duckdb_cursor.read_csv(string, header=True).fetchall()
		assert res == [('a', 'b', 'c')]
	
	def test_filelike_exception(self, duckdb_cursor):
		class ReadError:
			def __init__(self):
				pass
			def read(self, amount):
				raise ValueError(amount)
			def seek(self, loc):
				return 0

		class SeekError:
			def __init__(self):
				pass
			def read(self, amount):
				return b'test'
			def seek(self, loc):
				raise ValueError(loc)

		obj = ReadError()
		with pytest.raises(ValueError):
			res = duckdb_cursor.read_csv(obj, header=True).fetchall()

		obj = SeekError()
		with pytest.raises(ValueError):
			res = duckdb_cursor.read_csv(obj, header=True).fetchall()
	
	def test_filelike_custom(self, duckdb_cursor):
		class CustomIO:
			def __init__(self):
				self.loc = 0
				pass
			def seek(self, loc):
				self.loc = loc
				return loc
			def read(self, amount):
				out = b"c1,c2,c3\na,b,c"[self.loc : self.loc + amount : 1]
				self.loc += amount
				return out

		obj = CustomIO()
		res = duckdb_cursor.read_csv(obj, header=True).fetchall()
		assert res == [('a', 'b', 'c')]

	def test_filelike_non_readable(self, duckdb_cursor):
		obj = 5;
		with pytest.raises(ValueError, match="Can not read from a non file-like object"):
			res = duckdb_cursor.read_csv(obj, header=True).fetchall()
	
	def test_filelike_none(self, duckdb_cursor):
		obj = None;
		with pytest.raises(ValueError, match="Can not read from a non file-like object"):
			res = duckdb_cursor.read_csv(obj, header=True).fetchall()

	def test_internal_object_filesystem_cleanup(self, duckdb_cursor):
		class CountedObject(StringIO):
			instance_count = 0
			def __init__(self, str):
				CountedObject.instance_count += 1
				super().__init__(str)
			def __del__(self):
				CountedObject.instance_count -= 1

		def scoped_objects(duckdb_cursor):
			obj = CountedObject("a,b,c")
			rel1 = duckdb_cursor.read_csv(obj)
			assert rel1.fetchall() == [('a','b','c',)]
			assert CountedObject.instance_count == 1

			obj = CountedObject("a,b,c")
			rel2 = duckdb_cursor.read_csv(obj)
			assert rel2.fetchall() == [('a','b','c',)]
			assert CountedObject.instance_count == 2

			obj = CountedObject("a,b,c")
			rel3 = duckdb_cursor.read_csv(obj)
			assert rel3.fetchall() == [('a','b','c',)]
			assert CountedObject.instance_count == 3
		assert CountedObject.instance_count == 0
		scoped_objects(duckdb_cursor)
		assert CountedObject.instance_count == 0