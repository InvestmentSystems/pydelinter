import os
import re
import typing as tp
import collections
import dataclasses
from typing import Set
from typing import Dict
from typing import Union
from collections import defaultdict

import libcst as cst

unused_imports: Dict[Union[cst.Import, cst.ImportFrom], Set[str]] = defaultdict(set)
undefined_references: Dict[cst.CSTNode, Set[str]] = defaultdict(set)

pylint_str = str # output formatted string of Pylint output

@dataclasses.dataclass
class BaseWarning:
    file_path: str
    line_no: int

@dataclasses.dataclass
class BaseUnusedImportsWarning(BaseWarning):
    '''
    Sum type class to represent types
    '''
    pass

@dataclasses.dataclass
class UnusedFromImportsWarning(BaseUnusedImportsWarning):
    import_as_name: str
    dotted_as_name: str
    alias: str

@dataclasses.dataclass
class UnusedImportsWarning(BaseUnusedImportsWarning):
    alias: str
    dotted_as_name: str


class BaseDelinter:
    pass

class UnusedImportsDelinter(BaseDelinter):
    CODE = 'W0611'

    # filter import without alias
    pattern_import = re.compile('Unused import (?P<dname>.*)')
    # filter import with alias
    pattern_import_with_alias = re.compile('Unused (?P<dname>.*) imported as (?P<aname>.*)')

    # filter from with alias
    pattern_from_with_alias = re.compile(
            'Unused (?P<sub_dname>.*) imported from (?P<dname>.*) as (?P<aname>.*)')

    # filter from
    pattern_from = re.compile('Unused (?P<aname>.*) imported from (?P<dname>.*)')

    patterns = [
            (pattern_import, UnusedImportsWarning),
            (pattern_import_with_alias, UnusedImportsWarning),
            # the order of from filters is implicit here, to keep the regex simple.
            (pattern_from_with_alias, UnusedFromImportsWarning),
            (pattern_from, UnusedFromImportsWarning)]

    @classmethod
    def parse_linter_warning(cls,
            warning: tp.Iterable[tp.Tuple[str, int, pylint_str]]) -> BaseUnusedImportsWarning:
        '''
        Filter just the linter warnings
        '''
        file_path, line_no, warning = warning
        for pattern, class_ in cls.patterns:
            m = re.match(pattern, warning)
            if m:
                groups = m.groups()
                if class_ is UnusedImportsWarning:
                    if len(groups) == 2:
                        return UnusedImportsWarning(
                                file_path=file_path,
                                line_no=line_no,
                                alias=m.group('aname'),
                                dotted_as_name=m.group('dname')
                                )
                    return UnusedImportsWarning(
                            file_path=file_path,
                            line_no=line_no,
                            alias=None,
                            dotted_as_name=m.group('dname')
                            )

                if class_ is UnusedFromImportsWarning:
                    if len(groups) == 2:
                        return UnusedFromImportsWarning(
                                file_path=file_path,
                                line_no=line_no,
                                import_as_name=m.group('aname'),
                                dotted_as_name=m.group('dname'),
                                alias=None)
                    return UnusedFromImportsWarning(
                            file_path=file_path,
                            line_no=line_no,
                            import_as_name=m.group('sub_dname'),
                            dotted_as_name=m.group('dname'),
                            alias=m.group('aname'))
        raise ValueError(f"Parsing failed for {warning}")

    @classmethod
    def update(cls, cst, warnings):
        '''
        Apply the refactor on each of the linter warnings
        '''
        pass

class RemoveUnusedImportTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (cst.metadata.SyntacticPositionProvider, cst.metadata.BasicPositionProvider)

    def __init__(self, warnings: tp.Union[UnusedImportsWarning, UnusedFromImportsWarning]):
        self.warnings = warnings
        pass

    @classmethod
    def build_dotted_name(cls, import_alias: cst.Attribute):
        def walk(node):
            if isinstance(node, cst.Name):
                return (node.value,)
            children = walk(node.value)
            return children + (node.attr.value,)
        return walk(import_alias)

    def leave_import_alike(
        self,
        original_node: tp.Union[cst.Import, cst.ImportFrom],
        updated_node: tp.Union[cst.Import, cst.ImportFrom],
    ) -> tp.Union[cst.Import, cst.ImportFrom, cst.RemovalSentinel]:
        #import ipdb; ipdb.set_trace()
        pass

    def is_unused_import(self, line_no, import_node: cst.ImportAlias):
        for warning in self.warnings:
            if isinstance(warning, UnusedImportsWarning):
                dotted_name = ".".join(self.build_dotted_name(import_node.name))
                asname = None if not import_node.asname else import_node.asname.name.value
                if (warning.dotted_as_name == dotted_name
                        and warning.alias == asname):
                    if warning.line_no == line_no:
                        #import ipdb; ipdb.set_trace()
                        return True
                    else:
                        continue
                    #return True
        return False

    def is_unused_import_from(self, line_no: int, module: cst.Module, import_node: cst.ImportAlias):
        for warning in self.warnings:
            if isinstance(warning, UnusedFromImportsWarning):
                dotted_name = ".".join(self.build_dotted_name(module))
                asname = None if not import_node.asname else import_node.asname.name.value
                if (warning.dotted_as_name == dotted_name
                        and warning.import_as_name == import_node.name.value
                        and warning.line_no == line_no
                        and warning.alias == asname):
                    return True
        return False

    def leave_Import(
        self, original_node: cst.Import, updated_node: cst.Import
    ) -> cst.Import:

        code = self.get_metadata(cst.metadata.SyntacticPositionProvider, original_node)
        new_import_alias = []
        line_no = code.start.line
        for import_alias in updated_node.names:
            if self.is_unused_import(line_no, import_alias):
                continue
            new_import_alias.append(import_alias)
        if new_import_alias:
            new_import_alias[-1] = new_import_alias[-1].with_changes(
                    comma=cst.MaybeSentinel.DEFAULT)
            return updated_node.with_changes(names=new_import_alias)
        if len(new_import_alias) == 0:
            return cst.RemoveFromParent()
        return updated_node


    def leave_ImportFrom(
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> cst.ImportFrom:
        #import ipdb; ipdb.set_trace()
        code = self.get_metadata(cst.metadata.SyntacticPositionProvider, original_node)
        line_no = code.start.line
        new_import_alias = []
        if isinstance(updated_node.names, cst.ImportStar):
            # we do not handle ImportStar
            return updated_node
        for import_alias in updated_node.names:
            if self.is_unused_import_from(line_no, updated_node.module, import_alias):
                continue
            new_import_alias.append(import_alias)
        if new_import_alias:
            new_import_alias[-1] = new_import_alias[-1].with_changes(
                    comma=cst.MaybeSentinel.DEFAULT)
            return updated_node.with_changes(names=new_import_alias)
        if len(new_import_alias) == 0:
            return cst.RemoveFromParent()
        return updated_node
