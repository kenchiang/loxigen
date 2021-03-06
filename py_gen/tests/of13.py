#!/usr/bin/env python
# Copyright 2013, Big Switch Networks, Inc.
#
# LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
# the following special exception:
#
# LOXI Exception
#
# As a special exception to the terms of the EPL, you may distribute libraries
# generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
# that copyright and licensing notices generated by LoxiGen are not altered or removed
# from the LoxiGen Libraries and the notice provided below is (i) included in
# the LoxiGen Libraries, if distributed in source code form and (ii) included in any
# documentation for the LoxiGen Libraries, if distributed in binary form.
#
# Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
#
# You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
# a copy of the EPL at:
#
# http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# EPL for the specific language governing permissions and limitations
# under the EPL.
import unittest
import difflib

try:
    import loxi.of13 as ofp
    from loxi.generic_util import OFReader
except ImportError:
    exit("loxi package not found. Try setting PYTHONPATH.")

# Human-friendly format for binary strings. 8 bytes per line.
def format_binary(buf):
    byts = map(ord, buf)
    lines = [[]]
    for byt in byts:
        if len(lines[-1]) == 8:
            lines.append([])
        lines[-1].append(byt)
    return '\n'.join([' '.join(['%02x' % y for y in x]) for x in lines])

def diff(a, b):
    return '\n'.join(difflib.ndiff(a.splitlines(), b.splitlines()))

# Test serialization / deserialization of a sample object.
# Depends on the __eq__ method being correct.
def test_serialization(obj, buf):
    packed = obj.pack()
    if packed != buf:
        a = format_binary(buf)
        b = format_binary(packed)
        raise AssertionError("Serialization of %s failed\nExpected:\n%s\nActual:\n%s\nDiff:\n%s" % \
            (type(obj).__name__, a, b, diff(a, b)))
    unpacked = type(obj).unpack(buf)
    if obj != unpacked:
        a = obj.show()
        b = unpacked.show()
        raise AssertionError("Deserialization of %s failed\nExpected:\n%s\nActual:\n%s\nDiff:\n%s" % \
            (type(obj).__name__, a, b, diff(a, b)))

class TestImports(unittest.TestCase):
    def test_toplevel(self):
        import loxi
        self.assertTrue(hasattr(loxi, "ProtocolError"))
        self.assertEquals(loxi.version_names[4], "1.3")
        ofp = loxi.protocol(4)
        self.assertEquals(ofp.OFP_VERSION, 4)
        self.assertTrue(hasattr(ofp, "action"))
        self.assertTrue(hasattr(ofp, "common"))
        self.assertTrue(hasattr(ofp, "const"))
        self.assertTrue(hasattr(ofp, "message"))
        self.assertTrue(hasattr(ofp, "oxm"))

    def test_version(self):
        import loxi
        self.assertTrue(hasattr(loxi.of13, "ProtocolError"))
        self.assertTrue(hasattr(loxi.of13, "OFP_VERSION"))
        self.assertEquals(loxi.of13.OFP_VERSION, 4)
        self.assertTrue(hasattr(loxi.of13, "action"))
        self.assertTrue(hasattr(loxi.of13, "common"))
        self.assertTrue(hasattr(loxi.of13, "const"))
        self.assertTrue(hasattr(loxi.of13, "message"))
        self.assertTrue(hasattr(loxi.of13, "oxm"))

class TestCommon(unittest.TestCase):
    sample_hello_elem_buf = ''.join([
        '\x00\x01', # type
        '\x00\x0c', # length
        '\x01\x23\x45\x67', # bitmaps[0]
        '\x89\xab\xcd\xef', # bitmaps[1]
    ])

    def test_hello_elem_versionbitmap_pack(self):
        obj = ofp.hello_elem_versionbitmap(bitmaps=[ofp.uint32(0x01234567),ofp.uint32(0x89abcdef)])
        self.assertEquals(self.sample_hello_elem_buf, obj.pack())

    def test_hello_elem_versionbitmap_unpack(self):
        obj = ofp.hello_elem_versionbitmap.unpack(self.sample_hello_elem_buf)
        self.assertEquals(len(obj.bitmaps), 2)
        self.assertEquals(obj.bitmaps[0], ofp.uint32(0x01234567))
        self.assertEquals(obj.bitmaps[1], ofp.uint32(0x89abcdef))

    def test_list_hello_elem_unpack(self):
        buf = ''.join([
            '\x00\x01\x00\x04', # versionbitmap
            '\x00\x00\x00\x04', # unknown type
            '\x00\x01\x00\x04', # versionbitmap
        ])
        l = ofp.unpack_list_hello_elem(OFReader(buf))
        self.assertEquals(len(l), 2)
        self.assertTrue(isinstance(l[0], ofp.hello_elem_versionbitmap))
        self.assertTrue(isinstance(l[1], ofp.hello_elem_versionbitmap))

class TestMessages(unittest.TestCase):
    def test_hello(self):
        obj = ofp.message.hello(
            xid=0x12345678,
            elements=[
                ofp.hello_elem_versionbitmap(
                    bitmaps=[ofp.uint32(1), ofp.uint32(2)]),
                ofp.hello_elem_versionbitmap(
                    bitmaps=[ofp.uint32(3), ofp.uint32(4)])])
        buf = ''.join([
            '\x04', '\x00', # version, type
            '\x00\x20', # length
            '\x12\x34\x56\x78', # xid
            '\x00\x01', # elements[0].type
            '\x00\x0c', # elements[0].length
            '\x00\x00\x00\x01', # elements[0].bitmaps[0]
            '\x00\x00\x00\x02', # elements[0].bitmaps[1]
            '\x00\x01', # elements[1].type
            '\x00\x0c', # elements[1].length
            '\x00\x00\x00\x03', # elements[1].bitmaps[0]
            '\x00\x00\x00\x04', # elements[1].bitmaps[1]
        ])
        test_serialization(obj, buf)

    def test_error(self):
        obj = ofp.message.error_msg(
            xid=0x12345678,
            err_type=ofp.OFPET_BAD_MATCH,
            code=ofp.OFPBMC_BAD_MASK,
            data="abc")
        buf = ''.join([
            '\x04', '\x01', # version, type
            '\x00\x0f', # length
            '\x12\x34\x56\x78', # xid
            '\x00\x04', # err_type
            '\x00\x08', # code
            'abc', # data
        ])
        test_serialization(obj, buf)

    def test_echo_request(self):
        obj = ofp.message.echo_request(
            xid=0x12345678,
            data="abc")
        buf = ''.join([
            '\x04', '\x02', # version, type
            '\x00\x0b', # length
            '\x12\x34\x56\x78', # xid
            'abc', # data
        ])
        test_serialization(obj, buf)

    def test_echo_reply(self):
        obj = ofp.message.echo_reply(
            xid=0x12345678,
            data="abc")
        buf = ''.join([
            '\x04', '\x03', # version, type
            '\x00\x0b', # length
            '\x12\x34\x56\x78', # xid
            'abc', # data
        ])
        test_serialization(obj, buf)

    def test_features_request(self):
        obj = ofp.message.features_request(xid=0x12345678)
        buf = ''.join([
            '\x04', '\x05', # version, type
            '\x00\x08', # length
            '\x12\x34\x56\x78', # xid
        ])
        test_serialization(obj, buf)

    def test_features_reply(self):
        obj = ofp.message.features_reply(
            xid=0x12345678,
            datapath_id=0xFEDCBA9876543210,
            n_buffers=64,
            n_tables=200,
            auxiliary_id=5,
            capabilities=ofp.OFPC_FLOW_STATS|ofp.OFPC_PORT_BLOCKED,
            reserved=0)
        buf = ''.join([
            '\x04', '\x06', # version, type
            '\x00\x20', # length
            '\x12\x34\x56\x78', # xid
            '\xfe\xdc\xba\x98\x76\x54\x32\x10', # datapath_id
            '\x00\x00\x00\x40', # n_buffers
            '\xc8', # n_tables
            '\x05', # auxiliary_id
            '\x00\x00', # pad
            '\x00\x00\x01\x01', # capabilities
            '\x00\x00\x00\x00', # reserved
        ])
        test_serialization(obj, buf)

    def test_get_config_request(self):
        obj = ofp.message.get_config_request(xid=0x12345678)
        buf = ''.join([
            '\x04', '\x07', # version, type
            '\x00\x08', # length
            '\x12\x34\x56\x78', # xid
        ])
        test_serialization(obj, buf)

    def test_get_config_reply(self):
        obj = ofp.message.get_config_reply(
            xid=0x12345678,
            flags=ofp.OFPC_FRAG_REASM,
            miss_send_len=0xffff)
        buf = ''.join([
            '\x04', '\x08', # version, type
            '\x00\x0c', # length
            '\x12\x34\x56\x78', # xid
            '\x00\x02', # flags
            '\xff\xff', # miss_send_len
        ])
        test_serialization(obj, buf)

    def test_set_config(self):
        obj = ofp.message.set_config(
            xid=0x12345678,
            flags=ofp.OFPC_FRAG_REASM,
            miss_send_len=0xffff)
        buf = ''.join([
            '\x04', '\x09', # version, type
            '\x00\x0c', # length
            '\x12\x34\x56\x78', # xid
            '\x00\x02', # flags
            '\xff\xff', # miss_send_len
        ])
        test_serialization(obj, buf)

    def test_packet_in(self):
        obj = ofp.message.packet_in(
            xid=0x12345678,
            buffer_id=100,
            total_len=17000,
            reason=ofp.OFPR_ACTION,
            table_id=20,
            cookie=0xFEDCBA9876543210,
            match=ofp.match(oxm_list=[
                ofp.oxm.arp_op(value=1),
                ofp.oxm.in_port_masked(value=4, value_mask=5)]),
            data="abc")
        buf = ''.join([
            '\x04', '\x0a', # version, type
            '\x00\x35', # length
            '\x12\x34\x56\x78', # xid
            '\x00\x00\x00\x64', # buffer_id
            '\x42\x68', # total_len
            '\x01', # reason
            '\x14', # table_id
            '\xfe\xdc\xba\x98\x76\x54\x32\x10', # cookie
            '\x00\x01', # match.type
            '\x00\x16', # match.length
            '\x80\x00\x2A\x02', # match.oxm_list[0].type_len
            '\x00\x01', # match.oxm_list[0].value
            '\x80\x00\x01\x08', # match.oxm_list[1].type_len
            '\x00\x00\x00\x04', # match.oxm_list[1].value
            '\x00\x00\x00\x05', # match.oxm_list[1].mask
            '\x00\x00', # match.pad
            '\x00\x00', # pad
            'abc', # data
        ])
        test_serialization(obj, buf)

    def test_flow_removed(self):
        obj = ofp.message.flow_removed(
            xid=0x12345678,
            cookie=0xFEDCBA9876543210,
            priority=17000,
            reason=ofp.OFPRR_DELETE,
            table_id=20,
            duration_sec=10,
            duration_nsec=1000,
            idle_timeout=5,
            hard_timeout=30,
            packet_count=1,
            byte_count=2,
            match=ofp.match(oxm_list=[
                ofp.oxm.arp_op(value=1),
                ofp.oxm.in_port_masked(value=4, value_mask=5)]))
        buf = ''.join([
            '\x04', '\x0b', # version, type
            '\x00\x48', # length
            '\x12\x34\x56\x78', # xid
            '\xfe\xdc\xba\x98\x76\x54\x32\x10', # cookie
            '\x42\x68', # priority
            '\x02', # reason
            '\x14', # table_id
            '\x00\x00\x00\x0a', # duration_sec
            '\x00\x00\x03\xe8', # duration_nsec
            '\x00\x05', # idle_timeout
            '\x00\x1e', # hard_timeout
            '\x00\x00\x00\x00\x00\x00\x00\x01', # packet_count
            '\x00\x00\x00\x00\x00\x00\x00\x02', # byte_count
            '\x00\x01', # match.type
            '\x00\x16', # match.length
            '\x80\x00\x2A\x02', # match.oxm_list[0].type_len
            '\x00\x01', # match.oxm_list[0].value
            '\x80\x00\x01\x08', # match.oxm_list[1].type_len
            '\x00\x00\x00\x04', # match.oxm_list[1].value
            '\x00\x00\x00\x05', # match.oxm_list[1].mask
            '\x00\x00', # match.pad
        ])
        test_serialization(obj, buf)

    def test_port_status(self):
        obj = ofp.message.port_status(
            xid=0x12345678,
            reason=ofp.OFPPR_MODIFY,
            desc=ofp.port_desc(
                port_no=4,
                hw_addr=[1,2,3,4,5,6],
                name="foo",
                config=ofp.OFPPC_NO_FWD|ofp.OFPPC_NO_RECV,
                state=ofp.OFPPS_BLOCKED,
                curr=ofp.OFPPF_10MB_HD,
                advertised=ofp.OFPPF_10MB_FD,
                supported=ofp.OFPPF_100MB_HD,
                peer=ofp.OFPPF_100MB_FD,
                curr_speed=10,
                max_speed=20))
        buf = ''.join([
            '\x04', '\x0c', # version, type
            '\x00\x50', # length
            '\x12\x34\x56\x78', # xid
            '\x02', # reason
            '\x00' * 7, # pad
            '\x00\x00\x00\x04', # port_no
            '\x00' * 4, # pad
            '\x01\x02\x03\x04\x05\x06', # hw_addr
            '\x00' * 2, # pad
            'foo' + '\x00' * 13, # name
            '\x00\x00\x00\x24', # config
            '\x00\x00\x00\x02', # state
            '\x00\x00\x00\x01', # curr
            '\x00\x00\x00\x02', # advertised
            '\x00\x00\x00\x04', # supported
            '\x00\x00\x00\x08', # peer
            '\x00\x00\x00\x0a', # curr_speed
            '\x00\x00\x00\x14', # max_speed
        ])
        test_serialization(obj, buf)

    def test_packet_out(self):
        obj = ofp.message.packet_out(
            xid=0x12345678,
            buffer_id=100,
            in_port=4,
            actions=[
                ofp.action.output(port=2, max_len=0xffff),
                ofp.action.dec_nw_ttl()],
            data="abc")
        buf = ''.join([
            '\x04', '\x0d', # version, type
            '\x00\x33', # length
            '\x12\x34\x56\x78', # xid
            '\x00\x00\x00\x64', # buffer_id
            '\x00\x00\x00\x04', # in_port
            '\x00\x18', # actions_len
            '\x00' * 6, # pad
            '\x00\x00', # actions[0].type
            '\x00\x10', # actions[0].length
            '\x00\x00\x00\x02', # actions[0].port
            '\xff\xff', # actions[0].max_len
            '\x00' * 6, # pad
            '\x00\x18', # actions[1].type
            '\x00\x08', # actions[1].length
            '\x00' * 4, # pad
            'abc', # data
        ])
        test_serialization(obj, buf)


    ## Flow-mods

    def test_flow_add(self):
        obj = ofp.message.flow_add(
            xid=0x12345678,
            cookie=0xFEDCBA9876543210,
            cookie_mask=0xFF00FF00FF00FF00,
            table_id=3,
            idle_timeout=5,
            hard_timeout=10,
            priority=6000,
            buffer_id=50,
            out_port=6,
            out_group=8,
            flags=0,
            match=ofp.match(oxm_list=[]),
            instructions=[
                ofp.instruction.goto_table(table_id=4),
                ofp.instruction.goto_table(table_id=7)])
        buf = ''.join([
            '\x04', '\x0e', # version, type
            '\x00\x48', # length
            '\x12\x34\x56\x78', # xid

            '\xfe\xdc\xba\x98\x76\x54\x32\x10', # cookie

            '\xff\x00\xff\x00\xff\x00\xff\x00', # cookie_mask

            '\x03', # table_id
            '\x00', # _command
            '\x00\x05', # idle_timeout
            '\x00\x0a', # hard_timeout
            '\x17\x70', # priority

            '\x00\x00\x00\x32', # buffer_id
            '\x00\x00\x00\x06', # out_port

            '\x00\x00\x00\x08', # out_group
            '\x00\x00', # flags
            '\x00' * 2, # pad

            '\x00\x01', # match.type
            '\x00\x04', # match.length
            '\x00' * 4, # pad

            '\x00\x01', # instructions[0].type
            '\x00\x08', # instructions[0].length
            '\x04', # instructions[0].table_id
            '\x00' * 3, # pad

            '\x00\x01', # instructions[1].type
            '\x00\x08', # instructions[1].length
            '\x07', # instructions[1].table_id
            '\x00' * 3, # pad
        ])
        test_serialization(obj, buf)

    def test_flow_modify(self):
        # TODO
        pass

    def test_flow_modify_strict(self):
        # TODO
        pass

    def test_flow_delete(self):
        # TODO
        pass

    def test_flow_delete_strict(self):
        # TODO
        pass


    def test_group_mod(self):
        obj = ofp.message.group_mod(
            xid=0x12345678,
            command=ofp.OFPGC_MODIFY,
            group_type=ofp.OFPGT_FF,
            group_id=5,
            buckets=[
                ofp.bucket(
                    weight=1,
                    watch_port=5,
                    watch_group=0xffffffff,
                    actions=[
                        ofp.action.output(port=5, max_len=0),
                        ofp.action.output(port=6, max_len=0)]),
                ofp.bucket(
                    weight=1,
                    watch_port=6,
                    watch_group=0xffffffff,
                    actions=[
                        ofp.action.output(port=5, max_len=0),
                        ofp.action.output(port=6, max_len=0)])])
        buf = ''.join([
            '\x04', '\x0f', # version, type
            '\x00\x70', # length
            '\x12\x34\x56\x78', # xid
            '\x00\x01', # command
            '\x03', # group_type
            '\x00', # pad
            '\x00\x00\x00\x05', # group_id
            '\x00\x30', # buckets[0].len
            '\x00\x01', # buckets[0].weight
            '\x00\x00\x00\x05', # buckets[0].watch_port
            '\xff\xff\xff\xff', # buckets[0].watch_group
            '\x00' * 4, # pad
            '\x00\x00', # buckets[0].actions[0].type
            '\x00\x10', # buckets[0].actions[0].len
            '\x00\x00\x00\x05', # buckets[0].actions[0].port
            '\x00\x00', # buckets[0].actions[0].max_len
            '\x00' * 6, # pad
            '\x00\x00', # buckets[0].actions[1].type
            '\x00\x10', # buckets[0].actions[1].len
            '\x00\x00\x00\x06', # buckets[0].actions[1].port
            '\x00\x00', # buckets[0].actions[1].max_len
            '\x00' * 6, # pad
            '\x00\x30', # buckets[1].len
            '\x00\x01', # buckets[1].weight
            '\x00\x00\x00\x06', # buckets[1].watch_port
            '\xff\xff\xff\xff', # buckets[1].watch_group
            '\x00' * 4, # pad
            '\x00\x00', # buckets[1].actions[0].type
            '\x00\x10', # buckets[1].actions[0].len
            '\x00\x00\x00\x05', # buckets[1].actions[0].port
            '\x00\x00', # buckets[1].actions[0].max_len
            '\x00' * 6, # pad
            '\x00\x00', # buckets[1].actions[1].type
            '\x00\x10', # buckets[1].actions[1].len
            '\x00\x00\x00\x06', # buckets[1].actions[1].port
            '\x00\x00', # buckets[1].actions[1].max_len
            '\x00' * 6, # pad
        ])
        test_serialization(obj, buf)

    def test_port_mod(self):
        # TODO
        pass

    def test_table_mod(self):
        # TODO
        pass


    ## Multipart messages

    def test_desc_stats_request(self):
        # TODO
        pass

    def test_desc_stats_reply(self):
        # TODO
        pass

    def test_flow_stats_request(self):
        # TODO
        pass

    def test_flow_stats_reply(self):
        # TODO
        pass

    def test_aggregate_stats_request(self):
        # TODO
        pass

    def test_aggregate_stats_reply(self):
        # TODO
        pass

    def test_port_stats_request(self):
        # TODO
        pass

    def test_port_stats_reply(self):
        # TODO
        pass

    def test_queue_stats_request(self):
        # TODO
        pass

    def test_queue_stats_reply(self):
        # TODO
        pass

    def test_group_stats_request(self):
        # TODO
        pass

    def test_group_stats_reply(self):
        obj = ofp.message.group_stats_reply(
            xid=0x12345678,
            flags=0,
            entries=[
                ofp.group_stats_entry(
                    group_id=1,
                    ref_count=8,
                    packet_count=16,
                    byte_count=32,
                    duration_sec=20,
                    duration_nsec=100,
                    bucket_stats=[
                        ofp.bucket_counter(packet_count=1, byte_count=2),
                        ofp.bucket_counter(packet_count=3, byte_count=4)]),
                ofp.group_stats_entry(
                    group_id=1,
                    ref_count=8,
                    packet_count=16,
                    byte_count=32,
                    duration_sec=20,
                    duration_nsec=100,
                    bucket_stats=[])])
        buf = ''.join([
            '\x04', '\x13', # version, type
            '\x00\x80', # length
            '\x12\x34\x56\x78', # xid
            '\x00\x06', # stats_type
            '\x00\x00', # flags
            '\x00' * 4, # pad
            '\x00\x48', # entries[0].length
            '\x00' * 2, # pad
            '\x00\x00\x00\x01', # entries[0].group_id
            '\x00\x00\x00\x08', # entries[0].ref_count
            '\x00' * 4, # pad
            '\x00\x00\x00\x00\x00\x00\x00\x10', # entries[0].packet_count
            '\x00\x00\x00\x00\x00\x00\x00\x20', # entries[0].byte_count
            '\x00\x00\x00\x14', # entries[0].duration_sec
            '\x00\x00\x00\x64', # entries[0].duration_nsec
            '\x00\x00\x00\x00\x00\x00\x00\x01', # entries[0].bucket_stats[0].packet_count
            '\x00\x00\x00\x00\x00\x00\x00\x02', # entries[0].bucket_stats[0].byte_count
            '\x00\x00\x00\x00\x00\x00\x00\x03', # entries[0].bucket_stats[1].packet_count
            '\x00\x00\x00\x00\x00\x00\x00\x04', # entries[0].bucket_stats[1].byte_count
            '\x00\x28', # entries[0].length
            '\x00' * 2, # pad
            '\x00\x00\x00\x01', # entries[0].group_id
            '\x00\x00\x00\x08', # entries[0].ref_count
            '\x00' * 4, # pad
            '\x00\x00\x00\x00\x00\x00\x00\x10', # entries[0].packet_count
            '\x00\x00\x00\x00\x00\x00\x00\x20', # entries[0].byte_count
            '\x00\x00\x00\x14', # entries[0].duration_sec
            '\x00\x00\x00\x64', # entries[0].duration_nsec
        ])
        test_serialization(obj, buf)

    def test_group_desc_stats_request(self):
        # TODO
        pass

    def test_group_desc_stats_reply(self):
        obj = ofp.message.group_desc_stats_reply(
            xid=0x12345678,
            flags=0,
            entries=[
                ofp.group_desc_stats_entry(
                    type=ofp.OFPGT_FF,
                    group_id=1,
                    buckets=[
                        ofp.bucket(
                            weight=1,
                            watch_port=5,
                            watch_group=0xffffffff,
                            actions=[
                                ofp.action.output(port=5, max_len=0),
                                ofp.action.output(port=6, max_len=0)]),
                        ofp.bucket(
                            weight=1,
                            watch_port=6,
                            watch_group=0xffffffff,
                            actions=[
                                ofp.action.output(port=5, max_len=0),
                                ofp.action.output(port=6, max_len=0)])]),
                ofp.group_desc_stats_entry(type=ofp.OFPGT_FF, group_id=2, buckets=[])])
        buf = ''.join([
            '\x04', '\x13', # version, type
            '\x00\x80', # length
            '\x12\x34\x56\x78', # xid
            '\x00\x07', # stats_type
            '\x00\x00', # flags
            '\x00' * 4, # pad
            '\x00\x68', # entries[0].length
            '\x03', # entries[0].group_type
            '\x00', # entries[0].pad
            '\x00\x00\x00\x01', # entries[0].group_id
            '\x00\x30', # entries[0].buckets[0].len
            '\x00\x01', # entries[0].buckets[0].weight
            '\x00\x00\x00\x05', # entries[0].buckets[0].watch_port
            '\xff\xff\xff\xff', # entries[0].buckets[0].watch_group
            '\x00' * 4, # entries[0].pad
            '\x00\x00', # entries[0].buckets[0].actions[0].type
            '\x00\x10', # entries[0].buckets[0].actions[0].len
            '\x00\x00\x00\x05', # entries[0].buckets[0].actions[0].port
            '\x00\x00', # entries[0].buckets[0].actions[0].max_len
            '\x00' * 6, # entries[0].pad
            '\x00\x00', # entries[0].buckets[0].actions[1].type
            '\x00\x10', # entries[0].buckets[0].actions[1].len
            '\x00\x00\x00\x06', # entries[0].buckets[0].actions[1].port
            '\x00\x00', # entries[0].buckets[0].actions[1].max_len
            '\x00' * 6, # entries[0].pad
            '\x00\x30', # entries[0].buckets[1].len
            '\x00\x01', # entries[0].buckets[1].weight
            '\x00\x00\x00\x06', # entries[0].buckets[1].watch_port
            '\xff\xff\xff\xff', # entries[0].buckets[1].watch_group
            '\x00' * 4, # entries[0].pad
            '\x00\x00', # entries[0].buckets[1].actions[0].type
            '\x00\x10', # entries[0].buckets[1].actions[0].len
            '\x00\x00\x00\x05', # entries[0].buckets[1].actions[0].port
            '\x00\x00', # entries[0].buckets[1].actions[0].max_len
            '\x00' * 6, # entries[0].pad
            '\x00\x00', # entries[0].buckets[1].actions[1].type
            '\x00\x10', # entries[0].buckets[1].actions[1].len
            '\x00\x00\x00\x06', # entries[0].buckets[1].actions[1].port
            '\x00\x00', # entries[0].buckets[1].actions[1].max_len
            '\x00' * 6, # entries[0].pad
            '\x00\x08', # entries[1].length
            '\x03', # entries[1].group_type
            '\x00', # entries[1].pad
            '\x00\x00\x00\x02', # entries[1].group_id
        ])
        test_serialization(obj, buf)

    def test_group_features_stats_request(self):
        # TODO
        pass

    def test_group_features_stats_reply(self):
        # TODO
        pass

    def test_meter_stats_request(self):
        # TODO
        pass

    def test_meter_stats_reply(self):
        obj = ofp.message.meter_stats_reply(
            xid=0x12345678,
            flags=0,
            entries=[
                ofp.meter_stats(
                    meter_id=1,
                    flow_count=8,
                    packet_in_count=16,
                    byte_in_count=32,
                    duration_sec=20,
                    duration_nsec=100,
                    band_stats=[
                        ofp.meter_band_stats(packet_band_count=1, byte_band_count=2),
                        ofp.meter_band_stats(packet_band_count=3, byte_band_count=4)]),
                ofp.meter_stats(
                    meter_id=2,
                    flow_count=8,
                    packet_in_count=16,
                    byte_in_count=32,
                    duration_sec=20,
                    duration_nsec=100,
                    band_stats=[])])
        buf = ''.join([
            '\x04', '\x13', # version, type
            '\x00\x80', # length
            '\x12\x34\x56\x78', # xid
            '\x00\x09', # stats_type
            '\x00\x00', # flags
            '\x00' * 4, # pad
            '\x00\x00\x00\x01', # entries[0].meter_id
            '\x00\x48', # entries[0].len
            '\x00' * 6, # pad
            '\x00\x00\x00\x08', # entries[0].flow_count
            '\x00\x00\x00\x00\x00\x00\x00\x10', # entries[0].packet_in_count
            '\x00\x00\x00\x00\x00\x00\x00\x20', # entries[0].byte_in_count
            '\x00\x00\x00\x14', # entries[0].duration_sec
            '\x00\x00\x00\x64', # entries[0].duration_nsec
            '\x00\x00\x00\x00\x00\x00\x00\x01', # entries[0].band_stats[0].packet_band_count
            '\x00\x00\x00\x00\x00\x00\x00\x02', # entries[0].band_stats[0].byte_band_count
            '\x00\x00\x00\x00\x00\x00\x00\x03', # entries[0].band_stats[1].packet_band_count
            '\x00\x00\x00\x00\x00\x00\x00\x04', # entries[0].band_stats[1].byte_band_count
            '\x00\x00\x00\x02', # entries[1].meter_id
            '\x00\x28', # entries[1].len
            '\x00' * 6, # pad
            '\x00\x00\x00\x08', # entries[1].flow_count
            '\x00\x00\x00\x00\x00\x00\x00\x10', # entries[1].packet_in_count
            '\x00\x00\x00\x00\x00\x00\x00\x20', # entries[1].byte_in_count
            '\x00\x00\x00\x14', # entries[1].duration_sec
            '\x00\x00\x00\x64', # entries[1].duration_nsec
        ])
        test_serialization(obj, buf)

    def test_meter_config_stats_request(self):
        # TODO
        pass

    def test_meter_config_stats_reply(self):
        obj = ofp.message.meter_config_stats_reply(
            xid=0x12345678,
            flags=0,
            entries=[
                ofp.meter_band.drop(rate=1, burst_size=2),
                ofp.meter_band.dscp_remark(rate=3, burst_size=4, prec_level=5)])
        buf = ''.join([
            '\x04', '\x13', # version, type
            '\x00\x30', # length
            '\x12\x34\x56\x78', # xid
            '\x00\x0a', # stats_type
            '\x00\x00', # flags
            '\x00' * 4, # pad
            '\x00\x01', # entries[0].type
            '\x00\x10', # entries[0].length
            '\x00\x00\x00\x01', # entries[0].rate
            '\x00\x00\x00\x02', # entries[0].burst_size
            '\x00' * 4, # pad
            '\x00\x02', # entries[1].type
            '\x00\x10', # entries[1].length
            '\x00\x00\x00\x03', # entries[1].rate
            '\x00\x00\x00\x04', # entries[1].burst_size
            '\x05', # entries[1].prec_level
            '\x00' * 3, # pad
        ])
        test_serialization(obj, buf)

    def test_meter_features_stats_request(self):
        # TODO
        pass

    def test_meter_features_stats_reply(self):
        obj = ofp.message.meter_features_stats_reply(
            xid=0x12345678,
            flags=0,
            features=ofp.meter_features(
                max_meter=5,
                band_types=ofp.OFPMBT_DROP|ofp.OFPMBT_DSCP_REMARK,
                capabilities=ofp.OFPMF_KBPS|ofp.OFPMF_STATS,
                max_bands=10,
                max_color=7))
        buf = ''.join([
            '\x04', '\x13', # version, type
            '\x00\x20', # length
            '\x12\x34\x56\x78', # xid
            '\x00\x0b', # stats_type
            '\x00\x00', # flags
            '\x00' * 4, # pad
            '\x00\x00\x00\x05', # max_meter
            '\x00\x00\x00\x03', # band_types
            '\x00\x00\x00\x09', # capabilities
            '\x0a', # max_bands
            '\x07', # max_color
            '\x00' * 2, # pad
        ])
        test_serialization(obj, buf)

    def test_table_features_stats_request(self):
        # TODO
        pass

    def test_table_features_stats_reply(self):
        # TODO
        pass

    def test_port_desc_stats_request(self):
        # TODO
        pass

    def test_port_desc_stats_reply(self):
        # TODO
        pass


    def test_barrier_request(self):
        # TODO
        pass

    def test_barrier_reply(self):
        # TODO
        pass

    def test_queue_get_config_request(self):
        # TODO
        pass

    def test_queue_get_config_reply(self):
        # TODO
        pass

    def test_role_request(self):
        # TODO
        pass

    def test_role_reply(self):
        # TODO
        pass

    def test_get_async_request(self):
        # TODO
        pass

    def test_get_async_reply(self):
        # TODO
        pass

    def test_set_async(self):
        # TODO
        pass

    def test_meter_mod(self):
        # TODO
        pass

    # TODO test experimenter messages


class TestOXM(unittest.TestCase):
    def test_oxm_in_phy_port_pack(self):
        import loxi.of13 as ofp
        obj = ofp.oxm.in_phy_port(value=42)
        expected = ''.join([
            '\x80\x00', # class
            '\x02', # type/masked
            '\x04', # length
            '\x00\x00\x00\x2a' # value
        ])
        self.assertEquals(expected, obj.pack())

    def test_oxm_in_phy_port_masked_pack(self):
        import loxi.of13 as ofp
        obj = ofp.oxm.in_phy_port_masked(value=42, value_mask=0xaabbccdd)
        expected = ''.join([
            '\x80\x00', # class
            '\x03', # type/masked
            '\x08', # length
            '\x00\x00\x00\x2a', # value
            '\xaa\xbb\xcc\xdd' # mask
        ])
        self.assertEquals(expected, obj.pack())

    def test_oxm_ipv6_dst_pack(self):
        import loxi.of13 as ofp
        obj = ofp.oxm.ipv6_dst(value='\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0d\x0f')
        expected = ''.join([
            '\x80\x00', # class
            '\x36', # type/masked
            '\x10', # length
            '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0d\x0f', # value
        ])
        self.assertEquals(expected, obj.pack())

class TestInstructions(unittest.TestCase):
    def test_goto_table(self):
        obj = ofp.instruction.goto_table(table_id=5)
        buf = ''.join([
            '\x00\x01', # type
            '\x00\x08', # length
            '\x05', # table_id
            '\x00' * 3, # pad
        ])
        test_serialization(obj, buf)

    def test_write_metadata(self):
        # TODO
        pass

    def test_write_actions(self):
        # TODO
        pass

    def test_apply_actions(self):
        # TODO
        pass

    def test_clear_actions(self):
        # TODO
        pass

    def test_meter(self):
        # TODO
        pass

    # TODO test experimenter instructions

class TestAllOF13(unittest.TestCase):
    """
    Round-trips every class through serialization/deserialization.
    Not a replacement for handcoded tests because it only uses the
    default member values.
    """

    def setUp(self):
        mods = [ofp.action,ofp.message,ofp.common,ofp.oxm]
        self.klasses = [klass for mod in mods
                              for klass in mod.__dict__.values()
                              if hasattr(klass, 'show')]
        self.klasses.sort(key=lambda x: str(x))

    def test_serialization(self):
        expected_failures = [
            ofp.common.table_feature_prop_apply_actions,
            ofp.common.table_feature_prop_apply_actions_miss,
            ofp.common.table_feature_prop_write_actions,
            ofp.common.table_feature_prop_write_actions_miss,
            ofp.common.table_features,
            ofp.message.table_features_stats_reply,
            ofp.message.table_features_stats_request,
        ]
        for klass in self.klasses:
            def fn():
                obj = klass()
                if hasattr(obj, "xid"): obj.xid = 42
                buf = obj.pack()
                obj2 = klass.unpack(buf)
                self.assertEquals(obj, obj2)
            if klass in expected_failures:
                self.assertRaises(Exception, fn)
            else:
                fn()

    def test_show(self):
        expected_failures = []
        for klass in self.klasses:
            def fn():
                obj = klass()
                if hasattr(obj, "xid"): obj.xid = 42
                obj.show()
            if klass in expected_failures:
                self.assertRaises(Exception, fn)
            else:
                fn()

if __name__ == '__main__':
    unittest.main()
