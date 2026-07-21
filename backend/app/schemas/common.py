from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_code: str
    customer_name: str
    contact_person: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None
    remarks: str | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_code: str | None = None
    customer_name: str | None = None
    contact_person: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None
    remarks: str | None = None


class CustomerRead(CustomerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class ProjectBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: UUID
    project_type_id: int | None = None
    project_code: str
    project_name: str
    start_date: date | None = None
    end_date: date | None = None
    remarks: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: UUID | None = None
    project_type_id: int | None = None
    project_code: str | None = None
    project_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    remarks: str | None = None


class ProjectRead(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class VendorBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vendor_code: str
    vendor_name: str
    vendor_type: str
    contact_person: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None
    address_line: str | None = None
    remarks: str | None = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vendor_code: str | None = None
    vendor_name: str | None = None
    vendor_type: str | None = None
    contact_person: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None
    address_line: str | None = None
    remarks: str | None = None


class VendorRead(VendorBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
