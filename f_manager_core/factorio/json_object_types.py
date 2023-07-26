from datetime import datetime
from typing import List, Literal, Optional


class Links:
    first: str
    prev: str
    next: str
    last: str

    def __init__(self, json_data: dict):
        self.__dict__ = json_data

    def __repr__(self) -> str:
        return f"Links(first={self.first}, prev={self.prev}, next={self.next}, last={self.last})"


class Pagination:
    count: int
    links: Links
    page: int
    page_count: int
    page_size: int

    def __init__(self, json_data: dict):
        self.__dict__ = json_data

        self.links = Links(json_data["links"])

    def __repr__(self) -> str:
        return f"Pagination(count={self.count}, links={self.links}, page={self.page}, page_count={self.page_count}, page_size={self.page_size})"


class ModInfoShort:
    factorio_version: str
    dependencies: Optional[List[str]] = None

    def __init__(self, json_data: dict):
        self.__dict__ = json_data

    def __repr__(self) -> str:
        return f"ModInfoShort(factorio_version={self.factorio_version}, dependencies={self.dependencies})"


class Release:
    download_url: str
    file_name: str
    info_json: ModInfoShort
    released_at: datetime
    version: str
    sha1: str

    def __init__(self, json_data: dict):
        self.__dict__ = json_data

        self.released_at = datetime.fromisoformat(json_data["released_at"])

        self.info_json = ModInfoShort(json_data["info_json"])

    def __repr__(self) -> str:
        return f"Release(download_url={self.download_url}, file_name={self.file_name}, info_json={self.info_json}, released_at={self.released_at}, version={self.version}, sha1={self.sha1})"


class Tag:
    id: int
    name: str
    title: str
    description: str
    type: str

    def __init__(self, json_data: dict):
        self.__dict__ = json_data

    def __repr__(self) -> str:
        return f"Tag(id={self.id}, name={self.name}, title={self.title}, description={self.description}, type={self.type})"


class License:
    description: str
    id: str
    name: str
    title: str
    url: str

    def __init__(self, json_data: dict):
        self.__dict__ = json_data

    def __repr__(self) -> str:
        return f"License(description={self.description}, id={self.id}, name={self.name}, title={self.title}, url={self.url})"


class Result:
    downloads_count: int
    latest_release: Optional[Release] = None
    name: str
    owner: str
    releases: Optional[List[Release]] = None
    summary: str
    title: str
    category: Tag
    thumbnail: Optional[str] = None
    changelog: Optional[str] = None
    created_at: Optional[datetime] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    github_path: Optional[str] = None
    homepage: Optional[str] = None
    tag: Optional[List[Tag]] = None
    licence: Optional[List[License]] = None

    def __init__(self, json_data: dict):
        self.__dict__ = json_data

        if created_at := json_data.get("created_at"):
            self.created_at = datetime.fromisoformat(created_at)

        if latest_release := json_data.get("latest_release"):
            self.latest_release = Release(latest_release)

        if releases := json_data.get("releases"):
            self.releases = [Release(release) for release in releases]

        if tag := json_data.get("tag"):
            self.tag = [Tag(t) for t in tag]

        if license := json_data.get("licence"):
            self.licence = [License(l) for l in license]

    def __repr__(self) -> str:
        return f"Result(downloads_count={self.downloads_count}, latest_release={self.latest_release}, name={self.name}, owner={self.owner}, releases={self.releases}, summary={self.summary}, title={self.title}, category={self.category}, thumbnail={self.thumbnail}, changelog={self.changelog}, created_at={self.created_at}, description={self.description}, source_url={self.source_url}, github_path={self.github_path}, homepage={self.homepage}, tag={self.tag}, licence={self.licence})"


class ModListResponse:
    pagination: Optional[Pagination] = None
    results: List[Result]

    def __init__(self, json_data: dict):
        if pagination := json_data.get("pagination"):
            self.pagination = Pagination(pagination)
        self.results = [Result(result) for result in json_data["results"]]

    def __repr__(self) -> str:
        return f"ModListResponse(pagination={self.pagination}, results={self.results})"


################################################################################


class Category:
    title: str
    name: str
    desciption: str

    def __init__(self, json_data: list):
        self.title = json_data[0]
        self.name = json_data[1]
        self.desciption = json_data[2]

    def __repr__(self) -> str:
        return f"Category(title={self.title}, name={self.name}, desciption={self.desciption})"


################################################################################


class BookmarkToggleStatus:
    mod: str
    state: Literal["on", "off"]
    success: bool

    def __init__(self, json_data: dict):
        self.__dict__ = json_data

    def __repr__(self) -> str:
        return f"BookmarkToggleStatus(mod={self.mod}, state={self.state}, success={self.success})"
