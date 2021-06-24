# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: validator/service.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from validator import node_pb2 as validator_dot_node__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='validator/service.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x17validator/service.proto\x1a\x14validator/node.proto\"5\n\x0f\x41\x64\x64NodesRequest\x12\"\n\nvalidators\x18\x01 \x01(\x0b\x32\x0e.ValidatorList\"5\n\x0f\x44\x65lNodesRequest\x12\"\n\nvalidators\x18\x01 \x01(\x0b\x32\x0e.ValidatorList2n\n\x10ValidatorService\x12,\n\x08\x41\x64\x64Nodes\x12\x10.AddNodesRequest\x1a\x0e.ValidatorList\x12,\n\x08\x44\x65lNodes\x12\x10.DelNodesRequest\x1a\x0e.ValidatorListb\x06proto3'
  ,
  dependencies=[validator_dot_node__pb2.DESCRIPTOR,])




_ADDNODESREQUEST = _descriptor.Descriptor(
  name='AddNodesRequest',
  full_name='AddNodesRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='validators', full_name='AddNodesRequest.validators', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=49,
  serialized_end=102,
)


_DELNODESREQUEST = _descriptor.Descriptor(
  name='DelNodesRequest',
  full_name='DelNodesRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='validators', full_name='DelNodesRequest.validators', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=104,
  serialized_end=157,
)

_ADDNODESREQUEST.fields_by_name['validators'].message_type = validator_dot_node__pb2._VALIDATORLIST
_DELNODESREQUEST.fields_by_name['validators'].message_type = validator_dot_node__pb2._VALIDATORLIST
DESCRIPTOR.message_types_by_name['AddNodesRequest'] = _ADDNODESREQUEST
DESCRIPTOR.message_types_by_name['DelNodesRequest'] = _DELNODESREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

AddNodesRequest = _reflection.GeneratedProtocolMessageType('AddNodesRequest', (_message.Message,), {
  'DESCRIPTOR' : _ADDNODESREQUEST,
  '__module__' : 'validator.service_pb2'
  # @@protoc_insertion_point(class_scope:AddNodesRequest)
  })
_sym_db.RegisterMessage(AddNodesRequest)

DelNodesRequest = _reflection.GeneratedProtocolMessageType('DelNodesRequest', (_message.Message,), {
  'DESCRIPTOR' : _DELNODESREQUEST,
  '__module__' : 'validator.service_pb2'
  # @@protoc_insertion_point(class_scope:DelNodesRequest)
  })
_sym_db.RegisterMessage(DelNodesRequest)



_VALIDATORSERVICE = _descriptor.ServiceDescriptor(
  name='ValidatorService',
  full_name='ValidatorService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=159,
  serialized_end=269,
  methods=[
  _descriptor.MethodDescriptor(
    name='AddNodes',
    full_name='ValidatorService.AddNodes',
    index=0,
    containing_service=None,
    input_type=_ADDNODESREQUEST,
    output_type=validator_dot_node__pb2._VALIDATORLIST,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='DelNodes',
    full_name='ValidatorService.DelNodes',
    index=1,
    containing_service=None,
    input_type=_DELNODESREQUEST,
    output_type=validator_dot_node__pb2._VALIDATORLIST,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_VALIDATORSERVICE)

DESCRIPTOR.services_by_name['ValidatorService'] = _VALIDATORSERVICE

# @@protoc_insertion_point(module_scope)
