from typing import List

from globals import app, db
from constants.app_config import GROUPS_ENABLED
from src.misc import timestamp, get_arg_or_400, get_arg_or_none
from flask_login import login_required, current_user
from flask import render_template, request, redirect, url_for, flash, abort
from flask_babel import gettext
from forms import NewGroupFrom, SearchGroupForm
from libs.models.Group import Group
from libs.models.GroupMember import GroupMember
from libs.models.Invitation import InvitationType, Invitation


@app.route("/group", methods=['GET', 'POST'])
@login_required
def group_route():
    if not GROUPS_ENABLED:
        abort(403)

    if request.method == 'GET':
        action = get_arg_or_400('action')

        if action == 'my':
            return render_template('my_groups.html', groups=current_user.get_groups())

        elif action == 'new':
            new_group_form = NewGroupFrom()
            return render_template('new_group.html', form=new_group_form, groups=current_user.get_groups())
        elif action == 'search':
            search_group_form = SearchGroupForm()
            sport = get_arg_or_none('sport')
            if sport is None:
                groups = Group.query.limit(30).all()
            else:
                groups = Group.get_by_sport(sport)
            return render_template("search_group.html", query=groups, form=search_group_form)

        elif action == 'accept_invitation' or action == 'reject_invitation':
            group_id = get_arg_or_400('group_id')
            group: Group = Group.get_or_404(group_id)
            if current_user.id != group.admin_id:
                abort(403)
            invitation = Invitation.get_or_404(get_arg_or_400('id'))
            if action == 'accept_invitation':
                invitation.accept()
            else:
                invitation.reject()
            return redirect(url_for("group_route", action='invitations', id=group_id))

        group_id = get_arg_or_400('id', to_int=True)
        group = Group.get_or_404(group_id)
        members = group.get_members()
        is_member = current_user in members
        events = group.get_events()
        is_group_admin = group.admin_id == current_user.id
        if not is_member:
            is_member = None

        if action == 'delete' and is_group_admin:
            group.delete()
            return redirect(url_for('group_route', action='my'))

        elif action == 'edit' and is_group_admin:
            edit_group_form = NewGroupFrom(
                closed=group.closed,
                name=group.name,
                sport=group.sport
            )
            return render_template('edit_group.html', form=edit_group_form, group=group)

        elif action == 'show':
            return render_template(
                'group.html',
                group=group,
                members=members,
                is_member=is_member,
                events=events,
                is_group_admin=is_group_admin
            )

        elif action == 'invitations':
            group_invitations: List[Invitation] = Invitation.get_all_for_group(group_id)
            return render_template("group_invitations.html", invitations=group_invitations, group_id=group_id)

        elif action == 'join':
            if current_user not in members:
                if group.closed:
                    Invitation.add(type=InvitationType.TO_GROUP, recipient_id=group.id, referrer_id=current_user.id)
                    flash(gettext("Invitation sent!"), "success")
                else:
                    new_row = GroupMember(user_id=current_user.id, group_id=group.id, time=timestamp())
                    db.session.add(new_row)
                    db.session.commit()
                    members.append(current_user)
                    is_member = True
            return render_template(
                'group.html',
                group=group,
                members=members,
                is_member=is_member,
                events=events,
                is_group_admin=is_group_admin
            )

        elif action == 'leave':
            if current_user in members:
                row = GroupMember.query.filter_by(user_id=current_user.id, group_id=group.id).first()
                db.session.delete(row)
                db.session.commit()
                members.remove(current_user)
                is_member = None
            return render_template(
                'group.html',
                group=group,
                members=members,
                is_member=is_member,
                events=events,
                is_admin=is_group_admin
            )
        else:
            abort(403)

    else:
        action = get_arg_or_400('action')

        if action == 'edit':
            group_id = get_arg_or_400('id', to_int=True)
            group = Group.get_or_404(group_id)

            edit_group_form = NewGroupFrom(current_group=group)
            if edit_group_form.validate_on_submit():
                group.closed = edit_group_form.closed.data
                group.name = edit_group_form.name.data
                group.sport = edit_group_form.sport.data
                db.session.add(group)
                db.session.commit()
                return redirect(url_for('group_route', action='show', id=group_id))
            else:
                return render_template('edit_group.html', form=edit_group_form, group=group)

        elif action == 'new':
            new_group_form = NewGroupFrom()
            if new_group_form.validate_on_submit():
                group = Group(
                    admin_id=current_user.id,
                    name=new_group_form.name.data,
                    sport=new_group_form.sport.data,
                    closed=new_group_form.closed.data
                )
                db.session.add(group)
                db.session.commit()
                new_row = GroupMember(user_id=current_user.id, group_id=group.id, time=timestamp())
                db.session.add(new_row)
                db.session.commit()
                return redirect(url_for('group_route', action='show', id=group.id))
            else:
                return render_template('new_group.html', form=new_group_form, groups=current_user.get_groups())
        elif action == 'search':
            search_group_form = SearchGroupForm()
            name = search_group_form.name.data
            sport = search_group_form.sport.data
            groups = Group.query.filter(Group.name.ilike(f"%{name}%")). \
                filter(Group.sport == sport if sport != "None" else Group.sport == Group.sport).all()
            return render_template("search_group.html", query=groups, form=search_group_form)
        else:
            abort(400)
